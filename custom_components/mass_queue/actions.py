"""Actions for integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from music_assistant_models.errors import (
    InvalidCommand,
    MediaNotFoundError,
)

from .const import (
    ATTR_COMMAND,
    ATTR_DATA,
    ATTR_FAVORITE,
    ATTR_LIMIT,
    ATTR_LIMIT_AFTER,
    ATTR_LIMIT_BEFORE,
    ATTR_MEDIA_ALBUM_NAME,
    ATTR_MEDIA_ARTIST,
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_IMAGE,
    ATTR_MEDIA_TITLE,
    ATTR_OFFSET,
    ATTR_PLAYER_ENTITY,
    ATTR_QUEUE_ID,
    ATTR_QUEUE_ITEM_ID,
    DEFAULT_QUEUE_ITEMS_LIMIT,
    DEFAULT_QUEUE_ITEMS_OFFSET,
    DOMAIN,
    SERVICE_GET_QUEUE_ITEMS,
    SERVICE_MOVE_QUEUE_ITEM_DOWN,
    SERVICE_MOVE_QUEUE_ITEM_NEXT,
    SERVICE_MOVE_QUEUE_ITEM_UP,
    SERVICE_PLAY_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SERVICE_SEND_COMMAND,
)
from .controller import MassQueueController
from .schemas import (
    MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA,
    MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA,
    MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA,
    PLAY_QUEUE_ITEM_SERVICE_SCHEMA,
    QUEUE_ITEM_SCHEMA,
    QUEUE_ITEMS_SERVICE_SCHEMA,
    REMOVE_QUEUE_ITEM_SERVICE_SCHEMA,
    SEND_COMMAND_SERVICE_SCHEMA,
)

if TYPE_CHECKING:
    from music_assistant_client import MusicAssistantClient

    from . import MassQueueEntryData


class MassQueueActions:
    """Class to manage Music Assistant actions without passing `hass` and `mass_client` each time."""

    def __init__(self, hass: HomeAssistant, mass_client: MusicAssistantClient):
        """Initialize class."""
        self._hass: HomeAssistant = hass
        self._client: MusicAssistantClient = mass_client
        self._controller = MassQueueController(self._hass, self._client)

    def setup_controller(self):
        """Setup Music Assistant controller."""
        self._controller.update_players()
        self._controller.subscribe_events()
        self._hass.loop.create_task(self._controller.update_queues())

    @callback
    def register_actions(self) -> None:
        """Register actions with Home Assistant."""
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_GET_QUEUE_ITEMS,
            self.get_queue_items,
            schema=QUEUE_ITEMS_SERVICE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_PLAY_QUEUE_ITEM,
            self.play_queue_item,
            schema=PLAY_QUEUE_ITEM_SERVICE_SCHEMA,
            supports_response=SupportsResponse.NONE,
        )

        self._hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_QUEUE_ITEM,
            self.remove_queue_item,
            schema=REMOVE_QUEUE_ITEM_SERVICE_SCHEMA,
            supports_response=SupportsResponse.NONE,
        )
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_MOVE_QUEUE_ITEM_UP,
            self.move_queue_item_up,
            schema=MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA,
            supports_response=SupportsResponse.NONE,
        )
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_MOVE_QUEUE_ITEM_DOWN,
            self.move_queue_item_down,
            schema=MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA,
            supports_response=SupportsResponse.NONE,
        )
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_MOVE_QUEUE_ITEM_NEXT,
            self.move_queue_item_next,
            schema=MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA,
            supports_response=SupportsResponse.NONE,
        )
        self._hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_COMMAND,
            self.send_command,
            schema=SEND_COMMAND_SERVICE_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    def get_queue_id(self, entity_id: str):
        """Get the queue ID for a player."""
        return self._hass.states.get(entity_id).attributes[ATTR_QUEUE_ID]

    async def get_queue_index(self, entity_id: str):
        """Get the current index of the queue."""
        active_queue = await self.get_active_queue(entity_id)
        try:
            return active_queue.current_index or 0
        except AttributeError:
            return 0

    async def get_active_queue(self, entity_id: str):
        """Get active queue details."""
        queue_id = self.get_queue_id(entity_id)
        return await self._client.player_queues.get_active_queue(queue_id)

    def _format_queue_item(self, queue_item: dict) -> dict:
        """Format list of queue items for response."""
        queue_item = queue_item.to_dict()
        media = queue_item["media_item"]

        queue_item_id = queue_item["queue_item_id"]
        media_title = media["name"]
        media_album = media.get("album")
        media_album_name = "" if media_album is None else media_album.get("name", "")
        media_content_id = media["uri"]
        img = queue_item.get("image")
        media_image = "" if img is None else img.get("path", "")
        favorite = media["favorite"]

        artists = media["artists"]
        artist_names = [artist["name"] for artist in artists]
        media_artist = ", ".join(artist_names)
        response: ServiceResponse = QUEUE_ITEM_SCHEMA(
            {
                ATTR_QUEUE_ITEM_ID: queue_item_id,
                ATTR_MEDIA_TITLE: media_title,
                ATTR_MEDIA_ALBUM_NAME: media_album_name,
                ATTR_MEDIA_ARTIST: media_artist,
                ATTR_MEDIA_CONTENT_ID: media_content_id,
                ATTR_MEDIA_IMAGE: media_image,
                ATTR_FAVORITE: favorite,
            },
        )
        return response

    async def send_command(self, call: ServiceCall) -> ServiceResponse:
        """Sends command to Music Assistant and returns response."""
        command = call.data[ATTR_COMMAND]
        data = call.data.get(ATTR_DATA)
        response = await self._controller.send_command(command, data)
        return {"response": response}

    async def get_queue_items(self, call: ServiceCall) -> ServiceResponse:
        """Get all items in queue."""
        entity_id = call.data[ATTR_PLAYER_ENTITY]
        queue_id = self.get_queue_id(entity_id)
        if queue_id is None:
            return {entity_id: []}
        offset = call.data.get(ATTR_OFFSET)
        limit = call.data.get(ATTR_LIMIT)
        limit_before = call.data.get(ATTR_LIMIT_BEFORE)
        limit_after = call.data.get(ATTR_LIMIT_AFTER)
        idx = await self.get_queue_index(entity_id)
        if limit_before:
            offset = idx - limit_before
        if limit_after:
            limit = limit_before + limit_after + 1 if limit_before else limit_after + 1
        if offset is None:
            offset = idx + DEFAULT_QUEUE_ITEMS_OFFSET
        if limit is None:
            limit = DEFAULT_QUEUE_ITEMS_LIMIT
        offset = max(offset, 0)
        queue_items = await self._controller.player_queue(queue_id, limit, offset)
        response: ServiceResponse = {
            entity_id: [self._format_queue_item(item) for item in queue_items],
        }
        return response

    async def play_queue_item(self, call: ServiceCall) -> ServiceResponse:
        """Play selected item in queue."""
        entity_id = call.data[ATTR_PLAYER_ENTITY]
        queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
        queue_id = self.get_queue_id(entity_id)
        await self._client.send_command(
            "player_queues/play_index",
            queue_id=queue_id,
            index=queue_item_id,
        )

    async def remove_queue_item(self, call: ServiceCall) -> ServiceResponse:
        """Remove selected item from queue."""
        entity_id = call.data[ATTR_PLAYER_ENTITY]
        queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
        queue_id = self.get_queue_id(entity_id)
        await self._client.player_queues.queue_command_delete(queue_id, queue_item_id)

    async def move_queue_item_up(self, call: ServiceCall) -> ServiceResponse:
        """Move selected item up in queue."""
        entity_id = call.data[ATTR_PLAYER_ENTITY]
        queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
        queue_id = self.get_queue_id(entity_id)
        await self._client.player_queues.queue_command_move_up(queue_id, queue_item_id)

    async def move_queue_item_down(self, call: ServiceCall) -> ServiceResponse:
        """Move selected item down in queue."""
        entity_id = call.data[ATTR_PLAYER_ENTITY]
        queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
        queue_id = self.get_queue_id(entity_id)
        await self._client.player_queues.queue_command_move_down(
            queue_id,
            queue_item_id,
        )

    async def move_queue_item_next(self, call: ServiceCall) -> ServiceResponse:
        """Move selected item next in queue."""
        entity_id = call.data[ATTR_PLAYER_ENTITY]
        queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
        queue_id = self.get_queue_id(entity_id)
        await self._client.player_queues.queue_command_move_next(
            queue_id,
            queue_item_id,
        )

    async def unfavorite_item(self, call: ServiceCall) -> ServiceResponse:
        """Unfavorites currently playing item in queue."""
        entity_id = call.data[ATTR_PLAYER_ENTITY]
        attrs = self._hass.states.get(entity_id).attributes
        content_id = attrs.get(ATTR_MEDIA_CONTENT_ID)
        if not content_id:
            msg = f"Cannot find media with content id {content_id}"
            raise MediaNotFoundError(msg)
        provider = content_id.split("://")[0]
        if provider != "library":
            msg = f"Unfavorite can only apply to library media items, not from provider {provider}"
            raise InvalidCommand(msg)
        item_id = str(content_id.split("/")[-1])
        await self._client.send_command(
            "music/favorites/remove_item",
            media_type="track",
            library_item_id=item_id,
        )


@callback
def get_music_assistant_client(
    hass: HomeAssistant,
    entity_id: str,
) -> MusicAssistantClient:
    """Get Music Assistant client from entity_id."""
    registry = er.async_get(hass)
    entity = registry.async_get(entity_id)
    config_entry_id = entity.config_entry_id
    return _get_music_assistant_client(hass, config_entry_id)


@callback
def _get_music_assistant_client(
    hass: HomeAssistant,
    config_entry_id: str,
) -> MusicAssistantClient:
    """Get Music Assistant Client from config_entry_id."""
    entry: MassQueueEntryData | None
    if not (entry := hass.config_entries.async_get_entry(config_entry_id)):
        exc = "Entry not found."
        raise ServiceValidationError(exc)
    if entry.state is not ConfigEntryState.LOADED:
        exc = "Entry not loaded"
        raise ServiceValidationError(exc)
    return entry.runtime_data.mass


@callback
async def setup_controller_and_actions(
    hass: HomeAssistant,
    mass_client: MusicAssistantClient,
) -> MassQueueActions:
    """Initialize client and actions class, add actions to Home Assistant."""
    actions = MassQueueActions(hass, mass_client)
    actions.setup_controller()
    return actions
