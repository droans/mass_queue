"""Utilities."""

from __future__ import annotations

import base64
import urllib.parse
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import entity_registry as er

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from music_assistant_client import MusicAssistantClient

    from . import MassQueueEntryData

from .const import LOGGER


@callback
def _get_config_entry(
    hass: HomeAssistant,
    config_entry_id: str,
) -> MusicAssistantClient:
    """Get Music Assistant Client from config_entry_id."""
    entry: MassQueueEntryData | None
    if not (entry := hass.config_entries.async_get_entry(config_entry_id)):
        exc = "Entry not found."
        raise ServiceValidationError(exc)
    if entry.state is not ConfigEntryState.LOADED:
        exc = "Entry not loaded"
        raise ServiceValidationError(exc)
    return entry


def get_entity_actions_controller(hass, entity_id):
    """Gets the actions for the selected entity."""
    mass_entry = get_mass_entry(hass, entity_id)
    mass = mass_entry.runtime_data.mass.connection.ws_server_url
    mass_queue_entry = find_mass_queue_entry(hass, mass)
    return mass_queue_entry.runtime_data.actions


def get_mass_entry(hass, entity_id):
    """Helper function to pull MA Config Entry."""
    config_id = _get_mass_entity_config_entry_id(hass, entity_id)
    return _get_config_entry(hass, config_id)


def _get_mass_entity_config_entry_id(hass, entity_id):
    """Helper to grab config entry ID from entity ID."""
    registry = er.async_get(hass)
    return registry.async_get(entity_id).config_entry_id


def find_mass_queue_entry(hass, mass_url):
    """Finds the mass_queue entry for the given MA URL."""
    entries = _get_mass_queue_entries(hass)
    for entry in entries:
        entry_url = entry.runtime_data.mass.connection.ws_server_url
        if entry_url == mass_url:
            return entry
    msg = f"Cannot find entry for Music Assistant at {mass_url}"
    raise ServiceValidationError(msg)


def _get_mass_queue_entries(hass):
    """Gets all entries for mass_queue domain."""
    entries = hass.config_entries.async_entries()
    return [entry for entry in entries if entry.domain == "mass_queue"]


def format_event_data_queue_item(queue_item):
    """Format event data results for usage by controller."""
    if queue_item is None:
        return None
    if queue_item.get("queue_id") is None:
        return queue_item
    item_cp = queue_item.copy()
    if "streamdetails" in item_cp:
        item_cp.pop("streamdetails")
    if "media_item" in item_cp:
        item_cp.pop("media_item")
    return item_cp


def format_queue_updated_event_data(event: dict):
    """Format queue updated results for usage by controller."""
    event_data = event.copy()
    event_data["current_item"] = format_event_data_queue_item(
        event_data.get("current_item"),
    )
    event_data["next_item"] = format_event_data_queue_item(event_data.get("next_item"))
    return event_data


def get_queue_id_from_player_data(player_data):
    """Force as dict if not already."""
    data = player_data.to_dict() if type(player_data) is not dict else player_data
    current_media = data.get("current_media", None)
    if current_media is None:
        return None
    return current_media.get("queue_id")


def return_image_or_none(img_data: dict, remotely_accessible: bool):
    """Returns None if image is not present or not remotely accessible."""
    if type(img_data) is dict:
        img = img_data.get("path")
        remote = img_data.get("remotely_accessible")
        if remote or not remotely_accessible:
            return img
    return None


def search_image_list(images: list, remotely_accessible: bool):
    """Checks through a list of image data and attempts to find an image."""
    result = None
    for item in images:
        image = return_image_or_none(item, remotely_accessible)
        if image is not None:
            result = image
            break
    return result


def find_image_from_image(data: dict, remotely_accessible: bool):
    """Attempts to find the image via the image key."""
    img_data = data.get("image")
    return return_image_or_none(img_data, remotely_accessible)


def find_image_from_metadata(data: dict, remotely_accessible: bool):
    """Attempts to find the image via the metadata key."""
    media_item = data.get("media_item", {})
    metadata = media_item.get("metadata", {})
    img_data = metadata.get("images")
    if img_data is None:
        return None
    return search_image_list(img_data, remotely_accessible)


def find_image_from_album(data: dict, remotely_accessible: bool):
    """Attempts to find the image via the album key."""
    album = data.get("album", {})
    metadata = album.get("metadata", {})
    img_data = metadata.get("images")
    if img_data is None:
        return None
    return search_image_list(img_data, remotely_accessible)


def find_image_from_artists(data: dict, remotely_accessible: bool):
    """Attempts to find the image via the artists key."""
    artist = data.get("artist", {})
    img_data = artist.get("image")
    if img_data is list:
        return search_image_list(img_data, remotely_accessible)
    return return_image_or_none(img_data, remotely_accessible)


def find_image(data: dict, remotely_accessible: bool = True):
    """Returns None if image is not present or not remotely accessible."""
    from_image = find_image_from_image(data, remotely_accessible)
    from_metadata = find_image_from_metadata(data, remotely_accessible)
    from_album = find_image_from_album(data, remotely_accessible)
    from_artists = find_image_from_artists(data, remotely_accessible)
    return from_image or from_metadata or from_album or from_artists


def _get_recommendation_item_image_from_metadata(item: dict):
    try:
        images = item["metadata"]["images"]
        accessible = [image for image in images if image["remotely_accessible"]]
        if accessible:
            return accessible[0]["path"]
    except:  # noqa: E722
        LOGGER.debug(f"Unable to get images for item {item} from metadata.")
    return ""


def _get_recommendation_item_image_from_image(item: dict):
    try:
        image_data = item["image"]
        accessible = image_data["remotely_accessible"]
        if accessible:
            return image_data["path"]
    except:  # noqa: E722
        LOGGER.debug(f"Unable to get images for item {item} from image.")
    return ""


def _get_recommendation_item_image(item: dict):
    meta_img = _get_recommendation_item_image_from_metadata(item)
    img_img = _get_recommendation_item_image_from_image(item)
    if len(meta_img):
        return meta_img
    return img_img


def process_recommendation_section_item(item: dict):
    """Process and reformat a single recommendation item."""
    LOGGER.debug(f"Got section item: {item}")
    return {
        "item_id": item["item_id"],
        "name": item["name"],
        "sort_name": item["sort_name"],
        "uri": item["uri"],
        "media_type": item["media_type"],
        "image": _get_recommendation_item_image(item),
    }


def process_recommendation_section_items(items: list):
    """Process and reformat items for a single recommendation section."""
    return [process_recommendation_section_item(item) for item in items]


def process_recommendation_section(section: dict):
    """Process and reformat a single recommendation section."""
    LOGGER.debug(f"Got section: {section}")
    section = section.to_dict()
    return {
        "item_id": section["item_id"],
        "provider": section["provider"],
        "sort_name": section["sort_name"],
        "name": section["name"],
        "uri": section["uri"],
        "icon": section["icon"],
        "image": section["image"],
        "items": process_recommendation_section_items(section["items"]),
    }


def process_recommendations(recs: list):
    """Process and reformat items all recommendation sections."""
    result = []
    for rec in recs:
        processed = process_recommendation_section(rec)
        if len(processed["items"]):
            result.append(processed)
    return result


def generate_image_url_from_image_data(image_data: dict, client):
    """Generates an image URL from `image_data`."""
    img_path = image_data["path"]
    provider = image_data["provider"]
    base_url = "" if img_path.startswith("http") else client.server_url
    img = urllib.parse.quote_plus(urllib.parse.quote_plus(img_path))
    return f"{base_url}/imageproxy?provider={provider}&size=256&format=png&path={img}"


async def _download_single_image_from_image_data(
    image_data: dict,
    entity_id,
    hass,
    session,
):
    """Downloads a single image from Music Assistant and returns the base64 encoded string."""
    entry = get_mass_entry(hass, entity_id)
    client = entry.runtime_data.mass
    url = generate_image_url_from_image_data(image_data, client)
    try:
        req = await session.get(url)
        read = await req.content.read()
        return f"data:image;base64,{base64.b64encode(read).decode('utf-8')}"
    except:  # noqa: E722
        LOGGER.error(f"Unable to get image with data {image_data}")
        return None


@websocket_api.websocket_command(
    {
        vol.Required("type"): "mass_queue/encode_images",
        vol.Required("entity_id"): str,
        vol.Required("images"): list,
    },
)
@websocket_api.async_response
async def download_images(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Download images and return them as b64 encoded."""
    LOGGER.debug(f"Received message: {msg}")
    session = aiohttp_client.async_get_clientsession(hass)
    images = msg["images"]
    LOGGER.debug("Pulled images from message")
    LOGGER.debug(images)
    result = []
    entity_id = msg["entity_id"]
    for image in images:
        img = await _download_single_image_from_image_data(
            image,
            entity_id,
            hass,
            session,
        )
        image["encoded"] = img
        result.append(image)
    connection.send_result(msg["id"], result)


async def download_and_encode_image(url: str, hass: HomeAssistant):
    """Downloads and encodes a single image from the given URL."""
    session = aiohttp_client.async_get_clientsession(hass)
    req = await session.get(url)
    read = await req.content.read()
    return f"data:image;base64,{base64.b64encode(read).decode('utf-8')}"


@websocket_api.websocket_command(
    {
        vol.Required("type"): "mass_queue/download_and_encode_image",
        vol.Required("url"): str,
    },
)
@websocket_api.async_response
async def api_download_and_encode_image(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Download images and return them as b64 encoded."""
    LOGGER.debug(f"Got message: {msg}")
    url = msg["url"]
    LOGGER.debug(f"URL: {url}")
    result = await download_and_encode_image(url, hass)
    connection.send_result(msg["id"], result)
