"""Constants for the NEW_NAME integration."""

import logging

DOMAIN = "mass_queue"
DEFAULT_NAME = "Music Assistant Queue Items"
SERVICE_GET_QUEUE_ITEMS = "get_queue_items"
SERVICE_PLAY_QUEUE_ITEM = "play_queue_item"
SERVICE_REMOVE_QUEUE_ITEM = "remove_queue_item"
SERVICE_MOVE_QUEUE_ITEM_UP = "move_queue_item_up"
SERVICE_MOVE_QUEUE_ITEM_DOWN = "move_queue_item_down"
SERVICE_MOVE_QUEUE_ITEM_NEXT = "move_queue_item_next"
SERVICE_SEND_COMMAND = "send_command"
SERVICE_UNFAVORITE_CURRENT_ITEM = "unfavorite_current_item"
ATTR_QUEUE_ID = "active_queue"
ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_LIMIT = "limit"
ATTR_LIMIT_AFTER = "limit_after"
ATTR_LIMIT_BEFORE = "limit_before"
ATTR_QUEUE_ITEM_ID = "queue_item_id"
ATTR_MEDIA_TITLE = "media_title"
ATTR_MEDIA_ALBUM_NAME = "media_album_name"
ATTR_MEDIA_ARTIST = "media_artist"
ATTR_MEDIA_CONTENT_ID = "media_content_id"
ATTR_MEDIA_IMAGE = "media_image"
ATTR_OFFSET = "offset"
ATTR_PLAYER_ENTITY = "entity"
ATTR_QUEUE_ITEMS = "queue_items"
ATTR_COMMAND = "command"
ATTR_DATA = "data"
ATTR_FAVORITE = "favorite"
LOGGER = logging.getLogger(__package__)

DEFAULT_QUEUE_ITEMS_LIMIT = 500
DEFAULT_QUEUE_ITEMS_OFFSET = -5

MUSIC_ASSISTANT_EVENT_DOMAIN = "mass_music_assistant"
MASS_QUEUE_EVENT_DOMAIN = "mass_queue"
