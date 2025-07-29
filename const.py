"""Constants for the NEW_NAME integration."""
import logging

DOMAIN = "mass_queue_items"
DEFAULT_NAME = "Music Assistant Queue Items"
SERVICE_GET_QUEUE_ITEMS = "get_queue_items"
SERVICE_REMOVE_QUEUE_ITEM = "remove_queue_item"
SERVICE_MOVE_QUEUE_ITEM_UP = "move_queue_item_up"
SERVICE_MOVE_QUEUE_ITEM_DOWN = "move_queue_item_down"
SERVICE_MOVE_QUEUE_ITEM_NEXT = "move_queue_item_next"

ATTR_CONFIG_ENTRY_ID = "config_entry_id"

ATTR_PLAYER_ENTITY = "entity"
ATTR_OFFSET = "offset"
ATTR_LIMIT = "limit"
ATTR_QUEUE_ITEM_ID = "queue_item_id"
ATTR_MEDIA_TITLE = "media_title"
ATTR_MEDIA_ALBUM_NAME = "media_album_name"
ATTR_MEDIA_ARTIST = "media_artist"
ATTR_MEDIA_CONTENT_ID = "media_content_id"
ATTR_MEDIA_IMAGE = "media_image"
ATTR_QUEUE_ITEMS = "queue_items"
LOGGER = logging.getLogger(__package__)