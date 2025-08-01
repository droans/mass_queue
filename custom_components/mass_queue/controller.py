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
  ATTR_QUEUE_ITEM_ID,
  ATTR_MEDIA_TITLE,
  ATTR_MEDIA_ALBUM_NAME,
  ATTR_MEDIA_ARTIST,
  ATTR_MEDIA_CONTENT_ID,
  ATTR_MEDIA_IMAGE,
)
from .util import (
  get_changed_queues,
  get_changes_between_dicts,
  get_queue_id_from_player_data,
  format_queue_updated_event_data
)

from .schemas import QUEUE_ITEM_SCHEMA

class MassQueueController():
  def __init__(self, hass: HomeAssistant, mass_client):
    self._client = mass_client
    self._hass = hass
    self._queues = {}
    self._players = {}

  @property
  def players(self):
    return self._players
  
  @players.setter
  def players(self, players):
    LOGGER.debug(f'Got request to update players')
    if players == self._players:
      LOGGER.debug(f'No change to players')
      return
    LOGGER.debug(f'Got updated players: {players}')
    self.send_player_change_event(self._players, players)
    self._players = players
    
  def send_player_change_event(self, old_players, new_players):
    data = {}
    data['event_type'] = 'players_changed'
    data['data'] = get_changes_between_dicts(old_players, new_players)
    self.send_ha_event(data)

  @property
  def queues(self):
    return self._queues

  @queues.setter
  def queues(self, queues):
    LOGGER.debug(f'Got request to update queues')
    if queues == self._queues:
      LOGGER.debug(f'No change to queues')
      return
    LOGGER.debug(f'Got updated queues: {queues.keys()}')
    self.send_queue_change_event(self._queues, queues)
    self._queues = queues
    
  def send_queue_change_event(self, old_queue, new_queue):
    data = {}
    data['event_type'] = 'queues_changed'
    data['data'] = {'queues_changed': get_changed_queues(old_queue, new_queue)}
    LOGGER.debug(f'Got changed queues: {data['data']['queues_changed']}')
    self.send_ha_event(data)

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
    # TODO:
    # * Send HA Event when queue updated
    event_type = event.event
    event_object_id = event.object_id
    event_data = event.data
    event_queue_id = event_data.get('queue_id')
    self.update_queue_items(event_queue_id)
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
    # TODO:
    # * Send HA Event when queue items updated
    event_type = event.event
    event_object_id = event.object_id
    event_data = event.data
    event_queue_id = event_data.get('queue_id')
    self.update_queue_items(event_queue_id)
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
    # TODO:
    # * Send HA Event when player updated
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
    self.players = self.get_all_players()

  # Individual players
  def update_player_queue(self, player_id: str):
    player = self._client.players.get(player_id)
    if player is None:
      self.remove_player(player_id)
    queue_id = get_queue_id_from_player_data(player)
    self.players[player_id] = queue_id
    return
  
  async def get_player_queue(self, player_id: str):
    player = self._client.players.get(player_id)
    queue_id = get_queue_id_from_player_data(player)
    result = await self.get_queue(queue_id)
    return result

  def remove_player(self, player_id: str):
    if player_id in self.players:
      self.players.pop(player_id)
    return

  # All queues
  async def get_all_queues(self):
    queue_ids = [q.queue_id for q in self._client.player_queues.player_queues]
    result = {queue_id: await self.get_queue(queue_id) for queue_id in queue_ids}
    return result
  
  async def update_queues(self):
    self.queues = self.get_all_queues()
  
  # Individual queues
  async def player_queue(
      self, 
      queue_id: str, 
      limit: int = DEFAULT_QUEUE_ITEMS_LIMIT, 
      offset: int = DEFAULT_QUEUE_ITEMS_OFFSET
    ):
    queues = self.queues
    queue = queues.get(queue_id)
    if offset == -1:
      try:
        offset = await self.get_queue_index(queue_id) - 5
      except:
        offset = 0
    offset = max(offset, 0)
    result = queue[offset: offset + limit]
    return result
    
  async def update_queue_items(self, queue_id: str):
    queue = await self.get_queue(queue_id)
    self.queues[queue_id] = queue
    return

  def remove_queue(self, queue_id: str):
    if queue_id in self.queues:
      self.queues.pop(queue_id)
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
    queue_items = await self._client.get_player_queue_items(queue_id = queue_id, limit=limit, offset=offset)
    return queue_items

  async def get_active_queue(self, queue_id: str):
    result = await self._client.get_active_queue(queue_id)
    return result

  async def get_queue_index(self, queue_id: str):
    active_queue = await self.get_active_queue(queue_id)
    idx = active_queue.current_index
    return idx