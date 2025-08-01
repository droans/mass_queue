from __future__ import annotations

from homeassistant.core import (
  HomeAssistant
)
from music_assistant_models.enums import EventType

from .const import (
  DEFAULT_QUEUE_ITEMS_LIMIT,
  DEFAULT_QUEUE_ITEMS_OFFSET,
  LOGGER,
  EVENT_DOMAIN,
)
from .utils import (
  get_queue_id_from_player_data,
  format_queue_updated_event_data
)

class MassQueueController():
  def __init__(self, hass: HomeAssistant, mass_client):
    self._client = mass_client
    self._hass = hass
    self.players = Players(hass)
    self.queues = Queues(hass)

  # Events 
  def subscribe_events(self):
    self._client.subscribe(self.on_queue_update_event, EventType.QUEUE_UPDATED)
    self._client.subscribe(self.on_queue_items_update_event, EventType.QUEUE_ITEMS_UPDATED)
    self._client.subscribe(self.on_player_event, EventType.PLAYER_UPDATED)
    return 

  def send_ha_event(self, event_data):
    LOGGER.debug(f'Sending event type {EVENT_DOMAIN}, data {event_data}')
    self._hass.bus.async_fire(EVENT_DOMAIN, event_data)
    return

  def on_queue_update_event(self, event):
    LOGGER.debug(f'Got updated queue.')
    event_type = event.event
    event_object_id = event.object_id
    event_data = event.data
    event_queue_id = event_data.get('queue_id')
    self._hass.loop.create_task(self.update_queue_items(event_queue_id))
    if event_data is None:
      LOGGER.error(f'Event data is empty! Event: {event}')
      return
    data = format_queue_updated_event_data(event_data)
    ha_event_data = {
      'type': event_type,
      'object_id': event_object_id,
      'data': data
    }
    self.send_ha_event(ha_event_data)

  def on_queue_items_update_event(self, event):
    LOGGER.debug(f'Got updated queue items.')
    event_type = event.event
    event_object_id = event.object_id
    event_data = event.data
    event_queue_id = event_data.get('queue_id')
    self._hass.loop.create_task(self.update_queue_items(event_queue_id))
    if event_data is None:
      LOGGER.error(f'Event data is empty! Event: {event}')
      return
    data = format_queue_updated_event_data(event_data)
    ha_event_data = {
      'type': event_type,
      'object_id': event_object_id,
      'data': data
    }
    self.send_ha_event(ha_event_data)

  def on_player_event(self, event):
    event_type = event.event
    event_object_id = event.object_id
    event_data = event.data
    event_player = event_data['player_id']
    self.update_player_queue(event_player)
    if event_data is None:
      LOGGER.error(f'Event data is empty! Event: {event}')
      return
    ha_event_data = {
      'type': event_type,
      'object_id': event_object_id,
      'data': event.data
    }
    self.send_ha_event(ha_event_data)

  # All players
  def get_all_players(self):
    players = self._client.players.players
    result = {}
    for player_data in players:
      player_id = player_data.player_id
      queue_id = get_queue_id_from_player_data(player_data)
      result[player_id] = queue_id
    return result

  def update_players(self):
    LOGGER.debug(f'Updating all players.')
    players = self.get_all_players()
    self.players.batch_add(players)

  # Individual players
  def update_player_queue(self, player_id: str):
    LOGGER.debug(f'Updating player {player_id}.')
    player = self._client.players.get(player_id)
    if player is None:
      self.players.remove(player_id)
    queue_id = get_queue_id_from_player_data(player)
    self.players.update(player_id, queue_id)
    return
  
  async def get_player_queue(self, player_id: str):
    player = self._client.players.get(player_id)
    queue_id = get_queue_id_from_player_data(player)
    result = await self.get_queue(queue_id)
    return result

  # All queues
  async def get_all_queues(self):
    queue_ids = [q.queue_id for q in self._client.player_queues.player_queues]
    result = {queue_id: await self.get_queue(queue_id) for queue_id in queue_ids}
    return result
  
  async def update_queues(self):
    LOGGER.debug(f'Updating all queues.')
    queues = await self.get_all_queues()
    self.queues.batch_add(queues)
  
  # Individual queues
  async def player_queue(
      self, 
      queue_id: str, 
      limit: int = DEFAULT_QUEUE_ITEMS_LIMIT, 
      offset: int = DEFAULT_QUEUE_ITEMS_OFFSET
    ):
    queue = self.queues.get(queue_id)
    if offset == -1:
      try:
        offset = await self.get_queue_index(queue_id) - 5
      except:
        offset = 0
    offset = max(offset, 0)
    result = queue[offset: offset + limit]
    return result
    
  async def update_queue_items(self, queue_id: str):
    LOGGER.debug(f'Updating queue {queue_id}.')
    queue = await self.get_queue(queue_id)
    self.queues.update(queue_id, queue)
    return

  async def get_queue(
      self, 
      queue_id: str, 
      limit: int = DEFAULT_QUEUE_ITEMS_LIMIT, 
      offset: int = DEFAULT_QUEUE_ITEMS_OFFSET
    ):
    if offset == -1:
      try:
        offset = await self.get_queue_index(queue_id) - 5
      except:
        offset = 0
    offset = max(offset, 0)
    queue_items = await self._client.player_queues.get_player_queue_items(queue_id = queue_id, limit=limit, offset=offset)
    return queue_items

  async def get_active_queue(self, queue_id: str):
    result = await self._client.get_active_queue(queue_id)
    return result

  async def get_queue_index(self, queue_id: str):
    active_queue = await self.get_active_queue(queue_id)
    idx = active_queue.current_index
    return idx

class Players():
  def __init__(self, hass: HomeAssistant, players: dict = {}):
    self.players = players
    self._hass = hass
  def get(self, player_id):
    return self.players.get(player_id)
  def add(self, player_id: str, queue_id: str | None):
    self.players[player_id] = queue_id
    event_data = {
      'type': 'player_added',
      'data': {
        'player_id': player_id,
        'queue_id': queue_id
      }
    }
    self.send_ha_event(event_data)
  def batch_add(self, players: dict):
    for k, v in players.items():
      self.players[k] = v
    event_data = {
      'type': 'player_added',
      'data': {
        'players': players
      }
    }
    self.send_ha_event(event_data)
    
  def remove(self, player_id: str):
    if player_id in self.players:
      self.players.pop(player_id)
    event_data = {
      'type': 'player_removed',
      'data': {
        'player_id': player_id,
      }
    }
    self.send_ha_event(event_data)
  def update(self, player_id: str, queue_id: str):
    if player_id not in self.players:
      return
    current_queue_id = self.players[player_id]
    if current_queue_id == queue_id:
      pass
    self.players[player_id] = queue_id
    event_data = {
      'type': 'player_updated',
      'data': {
        'player_id': player_id,
        'queue_id': queue_id
      }
    }
    self.send_ha_event(event_data)
  def send_ha_event(self, event_data):
    LOGGER.debug(f'Sending event type {EVENT_DOMAIN}, data {event_data}')
    self._hass.bus.async_fire(EVENT_DOMAIN, event_data)
    return

class Queues():
  def __init__(self, hass: HomeAssistant, queues: dict = {}):
    self.queues = queues
    self._hass = hass
    return
  def get(self, queue_id):
    return self.queues[queue_id]
  def add(self, queue_id: str, queue_items: int):
    self.queues[queue_id] = queue_items
    event_data = {
      'type': 'queue_added',
      'data': {
        'queue_id': queue_id
      }
    }
    self.send_ha_event(event_data)
  def batch_add(self, queues):
    for k, v in queues.items():
      self.queues[k] = v
    event_data = {
      'type': 'queues_added',
      'data': {
        'queue_id': list(queues.keys())
      }
    }
    self.send_ha_event(event_data)
    
  def update(self, queue_id, queue_items):
    self.queues[queue_id] = queue_items
    event_data = {
      'type': 'queue_updated',
      'data': {
        'queue_id': queue_id
      }
    }
    self.send_ha_event(event_data)
  def remove(self, queue_id):
    if queue_id not in self.queues:
      return
    self.queues.pop(queue_id)
    event_data = {
      'type': 'queue_removed',
      'data': {
        'queue_id': queue_id
      }
    }
    self.send_ha_event(event_data)

  def send_ha_event(self, event_data):
    LOGGER.debug(f'Sending event type {EVENT_DOMAIN}, data {event_data}')
    self._hass.bus.async_fire(EVENT_DOMAIN, event_data)
    return