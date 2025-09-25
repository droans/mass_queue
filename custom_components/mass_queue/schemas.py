"""Schemas."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_COMMAND,
    ATTR_CONFIG_ENTRY_ID,
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
    ATTR_QUEUE_ITEM_ID,
    ATTR_QUEUE_ITEMS,
)

QUEUE_ITEM_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_QUEUE_ITEM_ID): str,
        vol.Required(ATTR_MEDIA_TITLE): str,
        vol.Required(ATTR_MEDIA_ALBUM_NAME): str,
        vol.Required(ATTR_MEDIA_ARTIST): str,
        vol.Required(ATTR_MEDIA_CONTENT_ID): str,
        vol.Required(ATTR_MEDIA_IMAGE): str,
        vol.Required(ATTR_FAVORITE): bool,
    },
)

QUEUE_DETAILS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_QUEUE_ITEMS): vol.All(
            cv.ensure_list,
            [vol.Schema(QUEUE_ITEM_SCHEMA)],
        ),
    },
)

QUEUE_ITEMS_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLAYER_ENTITY): str,
        vol.Optional(ATTR_OFFSET): int,
        vol.Optional(ATTR_LIMIT): int,
        vol.Optional(ATTR_LIMIT_BEFORE): int,
        vol.Optional(ATTR_LIMIT_AFTER): int,
    },
)
PLAY_QUEUE_ITEM_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLAYER_ENTITY): str,
        vol.Required(ATTR_QUEUE_ITEM_ID): str,
    },
)
REMOVE_QUEUE_ITEM_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLAYER_ENTITY): str,
        vol.Required(ATTR_QUEUE_ITEM_ID): str,
    },
)
MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLAYER_ENTITY): str,
        vol.Required(ATTR_QUEUE_ITEM_ID): str,
    },
)
MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLAYER_ENTITY): str,
        vol.Required(ATTR_QUEUE_ITEM_ID): str,
    },
)
MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLAYER_ENTITY): str,
        vol.Required(ATTR_QUEUE_ITEM_ID): str,
    },
)

SEND_COMMAND_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_COMMAND): str,
        vol.Optional(ATTR_DATA, default={}): dict,
        vol.Required(ATTR_CONFIG_ENTRY_ID): str,
    },
)

UNFAVORITE_CURRENT_ITEM_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLAYER_ENTITY): str,
    },
)
