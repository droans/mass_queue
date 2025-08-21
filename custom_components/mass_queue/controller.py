"""Controller for queues, players cache."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
from music_assistant_models.enums import EventType

from .const import (
    DEFAULT_QUEUE_ITEMS_LIMIT,
    DEFAULT_QUEUE_ITEMS_OFFSET,
    LOGGER,
    MASS_QUEUE_EVENT_DOMAIN,
    MUSIC_ASSISTANT_EVENT_DOMAIN,
)
from .utils import format_queue_updated_event_data, get_queue_id_from_player_data


class MassQueueController:
    """Controller to hold methods, handle events, and control caches of players and queues."""

    def __init__(self, hass: HomeAssistant, mass_client):
        """Initialize class."""
        self._client = mass_client
        self._hass = hass
        self.players = Players(hass)
        self.queues = Queues(hass)

    # Events
    def subscribe_events(self):
        """Subscribe to Music Assistant events."""
        self._client.subscribe(self.on_queue_update_event, EventType.QUEUE_UPDATED)
        self._client.subscribe(
            self.on_queue_items_update_event,
            EventType.QUEUE_ITEMS_UPDATED,
        )
        self._client.subscribe(self.on_player_event, EventType.PLAYER_UPDATED)

    def send_ha_event(self, event_data):
        """Send event to Home Assistant."""
        LOGGER.debug(
            f"Sending event type {MUSIC_ASSISTANT_EVENT_DOMAIN}, data {event_data}",
        )
        self._hass.bus.async_fire(MUSIC_ASSISTANT_EVENT_DOMAIN, event_data)

    def on_queue_update_event(self, event):
        """Callback when queue update event is received."""
        LOGGER.debug("Got updated queue.")
        event_type = event.event
        event_object_id = event.object_id
        event_data = event.data
        event_queue_id = event_data.get("queue_id")
        self._hass.loop.create_task(self.update_queue_items(event_queue_id))
        if event_data is None:
            LOGGER.error(f"Event data is empty! Event: {event}")
            return
        data = format_queue_updated_event_data(event_data)
        ha_event_data = {"type": event_type, "object_id": event_object_id, "data": data}
        self.send_ha_event(ha_event_data)

    def on_queue_items_update_event(self, event):
        """Callback when queue items update event is received."""
        LOGGER.debug("Got updated queue items.")
        event_type = event.event
        event_object_id = event.object_id
        event_data = event.data
        event_queue_id = event_data.get("queue_id")
        self._hass.loop.create_task(self.update_queue_items(event_queue_id))
        if event_data is None:
            LOGGER.error(f"Event data is empty! Event: {event}")
            return
        data = format_queue_updated_event_data(event_data)
        ha_event_data = {"type": event_type, "object_id": event_object_id, "data": data}
        self.send_ha_event(ha_event_data)

    def on_player_event(self, event):
        """Callback when player event is received."""
        event_type = event.event
        event_object_id = event.object_id
        event_data = event.data
        event_player = event_data["player_id"]
        self.update_player_queue(event_player)
        if event_data is None:
            LOGGER.error(f"Event data is empty! Event: {event}")
            return
        ha_event_data = {
            "type": event_type,
            "object_id": event_object_id,
            "data": event.data,
        }
        self.send_ha_event(ha_event_data)

    # All players
    def get_all_players(self):
        """Get all Music Assistant players."""
        players = self._client.players.players
        result = {}
        for player_data in players:
            player_id = player_data.player_id
            queue_id = get_queue_id_from_player_data(player_data)
            result[player_id] = queue_id
        return result

    def update_players(self):
        """Update all Music Assistant players."""
        LOGGER.debug("Updating all players.")
        players = self.get_all_players()
        self.players.batch_add(players)

    # Individual players
    def update_player_queue(self, player_id: str):
        """Update queue items for single Music Assistant queue."""
        LOGGER.debug(f"Updating player {player_id}.")
        player = self._client.players.get(player_id)
        if player is None:
            self.players.remove(player_id)
        queue_id = get_queue_id_from_player_data(player)
        self.players.update(player_id, queue_id)

    async def send_command(self, command: str, data: dict | None = None):
        """Sends command to Music Assistant and returns response."""
        data = data if data else {}
        return await self._client.send_command(command, require_schema=None, **data)

    async def get_player_queue(self, player_id: str):
        """Gets queue items for single Music Assistant queue."""
        player = self._client.players.get(player_id)
        queue_id = get_queue_id_from_player_data(player)
        return await self.get_queue(queue_id)

    # All queues
    async def get_all_queues(self):
        """Gets queue items for all Music Assistant queues."""
        queue_ids = [q.queue_id for q in self._client.player_queues.player_queues]
        return {queue_id: await self.get_queue(queue_id) for queue_id in queue_ids}

    async def update_queues(self):
        """Update queue items for all Music Assistant queues."""
        LOGGER.debug("Updating all queues.")
        queues = await self.get_all_queues()
        self.queues.batch_add(queues)

    # Individual queues
    async def player_queue(
        self,
        queue_id: str,
        limit: int = DEFAULT_QUEUE_ITEMS_LIMIT,
        offset: int = DEFAULT_QUEUE_ITEMS_OFFSET,
    ):
        """Get the cached queue items for a single queue."""
        queue = self.queues.get(queue_id)
        if offset == -1:
            try:
                offset = await self.get_queue_index(queue_id) - 5
            except IndexError:
                offset = 0
        offset = max(offset, 0)
        return queue[offset : offset + limit]

    async def update_queue_items(self, queue_id: str):
        """Update the queue items for a single queue."""
        LOGGER.debug(f"Updating queue {queue_id}.")
        queue = await self.get_queue(queue_id)
        self.queues.update(queue_id, queue)

    async def get_queue(
        self,
        queue_id: str,
        limit: int = DEFAULT_QUEUE_ITEMS_LIMIT,
        offset: int = DEFAULT_QUEUE_ITEMS_OFFSET,
    ):
        """Get the queue items for a single queue."""
        if offset == -1:
            try:
                offset = await self.get_queue_index(queue_id) - 5
            except IndexError:
                offset = 0
        offset = max(offset, 0)
        return await self._client.player_queues.get_player_queue_items(
            queue_id=queue_id,
            limit=limit,
            offset=offset,
        )

    async def get_active_queue(self, queue_id: str):
        """Get the active queue for a single queue."""
        return await self._client.get_active_queue(queue_id)

    async def get_queue_index(self, queue_id: str):
        """Get the active queue index for a single queue."""
        active_queue = await self.get_active_queue(queue_id)
        return active_queue.current_index


class Players:
    """Class to hold all player caches."""

    def __init__(self, hass: HomeAssistant, players: dict | None = None):
        """Initialize class."""
        self.players = players if players is not None else {}
        self._hass = hass

    def get(self, player_id):
        """Returns cached player records."""
        return self.players.get(player_id)

    def add(self, player_id: str, queue_id: str | None):
        """Adds a single player."""
        self.players[player_id] = queue_id
        event_data = {
            "type": "player_added",
            "data": {"player_id": player_id, "queue_id": queue_id},
        }
        self.send_ha_event(event_data)

    def batch_add(self, players: dict):
        """Adds multiple players at once."""
        for k, v in players.items():
            self.players[k] = v
        event_data = {"type": "player_added", "data": {"players": players}}
        self.send_ha_event(event_data)

    def remove(self, player_id: str):
        """Removes a single player."""
        if player_id in self.players:
            self.players.pop(player_id)
        event_data = {
            "type": "player_removed",
            "data": {
                "player_id": player_id,
            },
        }
        self.send_ha_event(event_data)

    def update(self, player_id: str, queue_id: str):
        """Updates the queue ID of a single player."""
        if player_id not in self.players:
            return
        current_queue_id = self.players[player_id]
        if current_queue_id == queue_id:
            pass
        self.players[player_id] = queue_id
        event_data = {
            "type": "player_updated",
            "data": {"player_id": player_id, "queue_id": queue_id},
        }
        self.send_ha_event(event_data)

    def send_ha_event(self, event_data):
        """Send event to Home Assistant."""
        LOGGER.debug(f"Sending event type {MASS_QUEUE_EVENT_DOMAIN}, data {event_data}")
        self._hass.bus.async_fire(MASS_QUEUE_EVENT_DOMAIN, event_data)


class Queues:
    """Class to hold all queue caches."""

    def __init__(self, hass: HomeAssistant, queues: dict | None = None):
        """Initialize class."""
        self.queues = queues if queues else {}
        self._hass = hass

    def get(self, queue_id):
        """Returns cached queue records."""
        return self.queues[queue_id]

    def add(self, queue_id: str, queue_items: int):
        """Adds a single queue."""
        self.queues[queue_id] = queue_items
        event_data = {"type": "queue_added", "data": {"queue_id": queue_id}}
        self.send_ha_event(event_data)

    def batch_add(self, queues):
        """Adds multiple queues at once."""
        for k, v in queues.items():
            self.queues[k] = v
        event_data = {"type": "queues_added", "data": {"queue_id": list(queues.keys())}}
        self.send_ha_event(event_data)

    def update(self, queue_id, queue_items):
        """Updates queue items in record."""
        self.queues[queue_id] = queue_items
        event_data = {"type": "queue_updated", "data": {"queue_id": queue_id}}
        self.send_ha_event(event_data)

    def remove(self, queue_id):
        """Removes queue from record."""
        if queue_id not in self.queues:
            return
        self.queues.pop(queue_id)
        event_data = {"type": "queue_removed", "data": {"queue_id": queue_id}}
        self.send_ha_event(event_data)

    def send_ha_event(self, event_data):
        """Send event to Home Assistant."""
        LOGGER.debug(f"Sending event type {MASS_QUEUE_EVENT_DOMAIN}, data {event_data}")
        self._hass.bus.async_fire(MASS_QUEUE_EVENT_DOMAIN, event_data)
