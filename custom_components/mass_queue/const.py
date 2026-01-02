"""Constants for the NEW_NAME integration."""

import logging

AUTH_SCHEMA_VERSION = 28
HASSIO_DISCOVERY_SCHEMA_VERSION = 28

CONF_TOKEN = "token"  # noqa: S105

DOMAIN = "mass_queue"
DEFAULT_NAME = "Music Assistant Queue Items"
SERVICE_CLEAR_QUEUE_FROM_HERE = "clear_queue_from_here"
SERVICE_GET_GROUP_VOLUME = "get_group_volume"
SERVICE_GET_ALBUM_TRACKS = "get_album_tracks"
SERVICE_GET_ARTIST_TRACKS = "get_artist_tracks"
SERVICE_GET_PLAYLIST_TRACKS = "get_playlist_tracks"
SERVICE_GET_QUEUE_ITEMS = "get_queue_items"
SERVICE_GET_RECOMMENDATIONS = "get_recommendations"
SERVICE_PLAY_QUEUE_ITEM = "play_queue_item"
SERVICE_MOVE_QUEUE_ITEM_DOWN = "move_queue_item_down"
SERVICE_MOVE_QUEUE_ITEM_NEXT = "move_queue_item_next"
SERVICE_MOVE_QUEUE_ITEM_UP = "move_queue_item_up"
SERVICE_REMOVE_QUEUE_ITEM = "remove_queue_item"
SERVICE_SEND_COMMAND = "send_command"
SERVICE_SET_GROUP_VOLUME = "set_group_volume"
SERVICE_UNFAVORITE_CURRENT_ITEM = "unfavorite_current_item"

ATTR_COMMAND = "command"
ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_DATA = "data"
ATTR_FAVORITE = "favorite"
ATTR_LIMIT = "limit"
ATTR_LIMIT_AFTER = "limit_after"
ATTR_LIMIT_BEFORE = "limit_before"
ATTR_LOCAL_IMAGE_ENCODED = "local_image_encoded"
ATTR_MEDIA_ALBUM_NAME = "media_album_name"
ATTR_MEDIA_ARTIST = "media_artist"
ATTR_MEDIA_CONTENT_ID = "media_content_id"
ATTR_MEDIA_IMAGE = "media_image"
ATTR_MEDIA_TITLE = "media_title"
ATTR_OFFSET = "offset"
ATTR_PAGE = "page"
ATTR_PLAYER_ENTITY = "entity"
ATTR_URI = "uri"
ATTR_PROVIDERS = "providers"
ATTR_QUEUE_ID = "active_queue"
ATTR_QUEUE_ITEM_ID = "queue_item_id"
ATTR_QUEUE_ITEMS = "queue_items"
ATTR_VOLUME_LEVEL = "volume_level"

CONF_DOWNLOAD_LOCAL = "download_local"

LOGGER = logging.getLogger(__package__)

DEFAULT_QUEUE_ITEMS_LIMIT = 500
DEFAULT_QUEUE_ITEMS_OFFSET = -5

MUSIC_ASSISTANT_EVENT_DOMAIN = "mass_music_assistant"
MASS_QUEUE_EVENT_DOMAIN = "mass_queue"
