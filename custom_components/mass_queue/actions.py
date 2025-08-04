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
from music_assistant_client import MusicAssistantClient
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, entity_registry as er

from .controller import MassQueueController
from .const import (
  DOMAIN,
  SERVICE_GET_QUEUE_ITEMS,
  SERVICE_PLAY_QUEUE_ITEM,
  SERVICE_REMOVE_QUEUE_ITEM,
  SERVICE_MOVE_QUEUE_ITEM_UP,
  SERVICE_MOVE_QUEUE_ITEM_DOWN,
  SERVICE_MOVE_QUEUE_ITEM_NEXT,
  LOGGER,
  ATTR_QUEUE_ITEM_ID,
  ATTR_MEDIA_TITLE,
  ATTR_MEDIA_ALBUM_NAME,
  ATTR_MEDIA_ARTIST,
  ATTR_MEDIA_CONTENT_ID,
  ATTR_MEDIA_IMAGE,
  ATTR_PLAYER_ENTITY,
  ATTR_LIMIT,
  ATTR_OFFSET
)
from .schemas import (
  QUEUE_ITEM_SCHEMA,
  QUEUE_ITEMS_SERVICE_SCHEMA,
  PLAY_QUEUE_ITEM_SERVICE_SCHEMA,
  REMOVE_QUEUE_ITEM_SERVICE_SCHEMA,
  MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA,
  MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA,
  MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA,
)

if TYPE_CHECKING:
  from . import MassQueueEntryData

class MassQueueActions():
  def __init__(self, hass: HomeAssistant, mass_client: MusicAssistantClient):
    self._hass: HomeAssistant = hass
    self._client: MusicAssistantClient = mass_client
    self._controller = MassQueueController(self._hass, self._client)

  def setup_controller(self):
    self._controller.update_players()
    self._controller.subscribe_events()
    self._hass.loop.create_task(self._controller.update_queues())

  @callback
  def register_actions(self) -> None:
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

  def get_queue_id(self, entity_id: str):
    registry = er.async_get(self._hass)
    entity = registry.async_get(entity_id)
    return entity.unique_id

  async def get_queue_index(self, entity_id: str):
    active_queue = await self.get_active_queue(entity_id)
    idx = active_queue.current_index
    return idx

  async def get_active_queue(self, entity_id: str):
    queue_id = self.get_queue_id(entity_id)
    queue = await self._client.player_queues.get_active_queue(queue_id)
    return queue

  def _format_queue_item(self, queue_item: dict) -> dict:
    queue_item = queue_item.to_dict()
    media = queue_item['media_item']

    queue_item_id = queue_item['queue_item_id']
    media_title = media['name']
    media_album = media.get('album')
    if media_album is None:
      media_album_name = media_album.get('name', '')
    else:
      media_album_name = ''
    media_content_id = media['uri']
    if 'image' in queue_item:
      img = queue_item['image']
      media_image = img.get('path')
    else:
      media_image = ''

    artists = media['artists']
    artist_names = [artist['name'] for artist in artists]
    media_artist = ', '.join(artist_names)
    response: ServiceResponse = QUEUE_ITEM_SCHEMA(
      {
        ATTR_QUEUE_ITEM_ID: queue_item_id,
        ATTR_MEDIA_TITLE: media_title,
        ATTR_MEDIA_ALBUM_NAME: media_album_name,
        ATTR_MEDIA_ARTIST: media_artist,
        ATTR_MEDIA_CONTENT_ID: media_content_id,
        ATTR_MEDIA_IMAGE: media_image
      }
    )
    return response
  async def get_queue_items(self, call: ServiceCall) -> ServiceResponse:
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    queue_id = self.get_queue_id(entity_id)
    limit = call.data.get(ATTR_LIMIT, 500)
    offset = call.data.get(ATTR_OFFSET, -1)
    if offset == -1:
      try:
        offset = await self.get_queue_index(entity_id) - 5
      except:
        offset = 0
      offset = max(offset, 0)
    queue_items = await self._controller.player_queue(queue_id, limit, offset)
    response: ServiceResponse = {
        entity_id: [self._format_queue_item(item) for item in queue_items]
      }
    return response
  
  async def play_queue_item(self, call: ServiceCall) -> ServiceResponse:
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
    queue_id = self.get_queue_id(entity_id)
    await self._client.send_command('player_queues/play_index', queue_id=queue_id, index=queue_item_id)
  
  async def remove_queue_item(self, call: ServiceCall) -> ServiceResponse:
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
    queue_id = self.get_queue_id(entity_id)
    await self._client.player_queues.queue_command_delete(queue_id, queue_item_id)
  
  async def move_queue_item_up(self, call: ServiceCall) -> ServiceResponse:
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
    queue_id = self.get_queue_id(entity_id)
    await self._client.player_queues.queue_command_move_up(queue_id, queue_item_id)
  
  async def move_queue_item_down(self, call: ServiceCall) -> ServiceResponse:
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
    queue_id = self.get_queue_id(entity_id)
    await self._client.player_queues.queue_command_move_down(queue_id, queue_item_id)
  
  async def move_queue_item_next(self, call: ServiceCall) -> ServiceResponse:
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
    queue_id = self.get_queue_id(entity_id)
    await self._client.player_queues.queue_command_move_next(queue_id, queue_item_id)
  
@callback
def get_music_assistant_client_boostrap(hass: HomeAssistant) -> MusicAssistantClient:
  mass_domain = 'music_assistant'
  entries = hass.config_entries.async_entries()
  config_entry = [entry for entry in entries if entry.domain == mass_domain][0]
  return config_entry.runtime_data.mass

@callback
def get_music_assistant_client(
  hass: HomeAssistant,
  entity_id: str) -> MusicAssistantClient:
  registry = er.async_get(hass)
  entity = registry.async_get(entity_id)
  config_entry_id = entity.config_entry_id
  return _get_music_assistant_client(hass, config_entry_id)

@callback
def _get_music_assistant_client(
  hass: HomeAssistant,
  config_entry_id: str) -> MusicAssistantClient:
  entry: MassQueueEntryData | None
  if not (entry := hass.config_entries.async_get_entry(config_entry_id)):
    raise ServiceValidationError("Entry not found")
  if entry.state is not ConfigEntryState.LOADED:
    raise ServiceValidationError("Entry not loaded")
  return entry.runtime_data.mass

@callback 
def setup_controller_and_actions(hass: HomeAssistant, mass_client: MusicAssistantClient|None = None) -> MassQueueActions:
  if mass_client is None:
    mass_client = get_music_assistant_client_boostrap(hass)
  actions = MassQueueActions(hass, mass_client)
  actions.setup_controller()
  actions.register_actions()
  return actions