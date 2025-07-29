from __future__ import annotations
from typing import TYPE_CHECKING
import voluptuous as vol

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

from .const import (
  DOMAIN,
  DEFAULT_NAME,
  SERVICE_GET_QUEUE_ITEMS,
  SERVICE_PLAY_QUEUE_ITEM,
  SERVICE_REMOVE_QUEUE_ITEM,
  SERVICE_MOVE_QUEUE_ITEM_UP,
  SERVICE_MOVE_QUEUE_ITEM_DOWN,
  SERVICE_MOVE_QUEUE_ITEM_NEXT,
  LOGGER,
  ATTR_QUEUE_ITEMS,
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
  QUEUE_DETAILS_SCHEMA, 
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

def _format_queue_item(queue_item: dict) -> dict:
  queue_item = queue_item.to_dict()
  media = queue_item['media_item']

  queue_item_id = queue_item['queue_item_id']
  media_title = media['name']
  media_album_name = media['album']['name']
  media_content_id = media['uri']
  media_image = queue_item['image']['path']

  artists = media['artists']
  artist_names = [artist['name'] for artist in artists]
  media_artist = ', '.join(artist_names)
  
  result = {
    ATTR_QUEUE_ITEM_ID: queue_item_id,
    ATTR_MEDIA_TITLE: media_title,
    ATTR_MEDIA_ALBUM_NAME: media_album_name,
    ATTR_MEDIA_ARTIST: media_artist,
    ATTR_MEDIA_CONTENT_ID: media_content_id,
    ATTR_MEDIA_IMAGE: media_image
  }
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

async def get_queue_items(call: ServiceCall) -> ServiceResponse:
  entity_id = call.data[ATTR_PLAYER_ENTITY]
  mass = get_music_assistant_client(call.hass, entity_id)
  queue_id = get_queue_id(call.hass, entity_id)
  limit = call.data.get(ATTR_LIMIT, 500)
  offset = call.data.get(ATTR_OFFSET, -1)
  if offset == -1:
    try:
      offset = await get_queue_index(call.hass, entity_id) - 5
    except:
      offset = 0
    offset = max(offset, 0)
  queue_items = await mass.player_queues.get_player_queue_items(queue_id = queue_id, limit = limit, offset = offset)
  response: ServiceResponse = {
      entity_id: [_format_queue_item(item) for item in queue_items]
    }
  return response

async def play_queue_item(call: ServiceCall) -> ServiceResponse:
  entity_id = call.data[ATTR_PLAYER_ENTITY]
  queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
  mass = get_music_assistant_client(call.hass, entity_id)
  queue_id = get_queue_id(call.hass, entity_id)
  await mass.send_command('player_queues/play_index', queue_id=queue_id, index=queue_item_id)

async def remove_queue_item(call: ServiceCall) -> ServiceResponse:
  entity_id = call.data[ATTR_PLAYER_ENTITY]
  queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
  mass = get_music_assistant_client(call.hass, entity_id)
  queue_id = get_queue_id(call.hass, entity_id)
  await mass.player_queues.queue_command_delete(queue_id, queue_item_id)

async def move_queue_item_up(call: ServiceCall) -> ServiceResponse:
  entity_id = call.data[ATTR_PLAYER_ENTITY]
  queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
  mass = get_music_assistant_client(call.hass, entity_id)
  queue_id = get_queue_id(call.hass, entity_id)
  await mass.player_queues.queue_command_move_up(queue_id, queue_item_id)
  
async def move_queue_item_down(call: ServiceCall) -> ServiceResponse:
  entity_id = call.data[ATTR_PLAYER_ENTITY]
  queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
  mass = get_music_assistant_client(call.hass, entity_id)
  queue_id = get_queue_id(call.hass, entity_id)
  await mass.player_queues.queue_command_move_down(queue_id, queue_item_id)
  
async def move_queue_item_next(call: ServiceCall) -> ServiceResponse:
  entity_id = call.data[ATTR_PLAYER_ENTITY]
  queue_item_id = call.data[ATTR_QUEUE_ITEM_ID]
  mass = get_music_assistant_client(call.hass, entity_id)
  queue_id = get_queue_id(call.hass, entity_id)
  await mass.player_queues.queue_command_move_next(queue_id, queue_item_id)

def get_queue_id(hass: HomeAssistant, entity_id: str):
  registry = er.async_get(hass)
  entity = registry.async_get(entity_id)
  return entity.unique_id

async def get_active_queue(hass: HomeAssistant, entity_id: str):
  queue_id = get_queue_id(hass, entity_id)
  mass = get_music_assistant_client(hass, entity_id)
  queue = await mass.player_queues.get_active_queue(queue_id)
  return queue

async def get_queue_index(hass: HomeAssistant, entity_id: str):
  active_queue = await get_active_queue(hass, entity_id)
  idx = active_queue.current_index
  return idx

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
def register_actions(hass: HomeAssistant) -> None:
  hass.services.async_register(
    DOMAIN,
    SERVICE_GET_QUEUE_ITEMS,
    get_queue_items,
    schema=QUEUE_ITEMS_SERVICE_SCHEMA,
    supports_response=SupportsResponse.ONLY,
  )
  hass.services.async_register(
    DOMAIN,
    SERVICE_PLAY_QUEUE_ITEM,
    play_queue_item,
    schema=PLAY_QUEUE_ITEM_SERVICE_SCHEMA,
    supports_response=SupportsResponse.NONE,
  )
  
  hass.services.async_register(
    DOMAIN,
    SERVICE_REMOVE_QUEUE_ITEM,
    remove_queue_item,
    schema=REMOVE_QUEUE_ITEM_SERVICE_SCHEMA,
    supports_response=SupportsResponse.NONE,
  )
  hass.services.async_register(
    DOMAIN,
    SERVICE_MOVE_QUEUE_ITEM_UP,
    move_queue_item_up,
    schema=MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA,
    supports_response=SupportsResponse.NONE,
  )
  hass.services.async_register(
    DOMAIN,
    SERVICE_MOVE_QUEUE_ITEM_DOWN,
    move_queue_item_down,
    schema=MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA,
    supports_response=SupportsResponse.NONE,
  )
  hass.services.async_register(
    DOMAIN,
    SERVICE_MOVE_QUEUE_ITEM_NEXT,
    move_queue_item_next,
    schema=MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA,
    supports_response=SupportsResponse.NONE,
  )
  