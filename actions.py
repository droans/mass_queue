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
  ATTR_CONFIG_ENTRY_ID,
  LOGGER,
  ATTR_QUEUE_ITEMS,
  ATTR_QUEUE_ITEM_ID,
  ATTR_MEDIA_TITLE,
  ATTR_MEDIA_ALBUM_NAME,
  ATTR_MEDIA_ARTIST,
  ATTR_MEDIA_CONTENT_ID,
  ATTR_MEDIA_IMAGE,
  ATTR_PLAYER_ENTITY
)
from .schemas import (
  QUEUE_DETAILS_SCHEMA, 
  QUEUE_ITEM_SCHEMA,
  QUEUE_ITEMS_SERVICE_SCHEMA
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
  mass = get_music_assistant_client(call.hass, call.data[ATTR_CONFIG_ENTRY_ID])
  registry = er.async_get(call.hass)
  entity = registry.async_get(entity_id)
  queue_id = entity.unique_id
  queue_items = await mass.player_queues.get_player_queue_items(queue_id)
  # result = {ATTR_QUEUE_ITEMS: [_format_queue_item(item) for item in queue_items]}
  response: ServiceResponse = QUEUE_DETAILS_SCHEMA(
    {
      ATTR_QUEUE_ITEMS: [_format_queue_item(item) for item in queue_items]
    }
  )
  LOGGER.fatal(f'Example: {response[ATTR_QUEUE_ITEMS][0]}')
  return response

@callback
def get_music_assistant_client(
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
  