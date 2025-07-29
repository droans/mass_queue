from __future__ import annotations

from typing import TYPE_CHECKING, Any
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import (
  ATTR_QUEUE_ITEM_ID,
  ATTR_MEDIA_TITLE,
  ATTR_MEDIA_ALBUM_NAME,
  ATTR_MEDIA_ARTIST,
  ATTR_MEDIA_CONTENT_ID,
  ATTR_MEDIA_IMAGE,
  ATTR_QUEUE_ITEMS,
  ATTR_CONFIG_ENTRY_ID,
  ATTR_PLAYER_ENTITY,
  ATTR_OFFSET,
  ATTR_LIMIT
)

QUEUE_ITEM_SCHEMA = vol.Schema(
  {
    vol.Required(ATTR_QUEUE_ITEM_ID): str,
    vol.Required(ATTR_MEDIA_TITLE): str,
    vol.Required(ATTR_MEDIA_ALBUM_NAME): str,
    vol.Required(ATTR_MEDIA_ARTIST): str,
    vol.Required(ATTR_MEDIA_CONTENT_ID): str,
    vol.Required(ATTR_MEDIA_IMAGE): str
  }
)

QUEUE_DETAILS_SCHEMA = vol.Schema(
  {
    vol.Required(ATTR_QUEUE_ITEMS): vol.All(cv.ensure_list, [vol.Schema(QUEUE_ITEM_SCHEMA)])
  }
)

QUEUE_ITEMS_SERVICE_SCHEMA = vol.Schema(
  {
    vol.Required(ATTR_PLAYER_ENTITY): str,
    vol.Optional(ATTR_OFFSET): int,
    vol.Optional(ATTR_LIMIT): int,

  }
)
REMOVE_QUEUE_ITEM_SERVICE_SCHEMA = vol.Schema(
  {
    vol.Required(ATTR_PLAYER_ENTITY): str,
    vol.Required(ATTR_QUEUE_ITEM_ID): str,

  }
)
MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA = vol.Schema(
  {
    vol.Required(ATTR_PLAYER_ENTITY): str,
    vol.Required(ATTR_QUEUE_ITEM_ID): str,

  }
)
MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA = vol.Schema(
  {
    vol.Required(ATTR_PLAYER_ENTITY): str,
    vol.Required(ATTR_QUEUE_ITEM_ID): str,

  }
)
MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA = vol.Schema(
  {
    vol.Required(ATTR_PLAYER_ENTITY): str,
    vol.Required(ATTR_QUEUE_ITEM_ID): str,

  }
)