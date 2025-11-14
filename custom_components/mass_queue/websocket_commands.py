"""Music Assistant Queue Actions Websocket Commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.helpers import aiohttp_client

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .const import LOGGER
from .utils import (
    download_and_encode_image,
    download_single_image_from_image_data,
    get_entity_info,
)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "mass_queue/get_info",
        vol.Required("entity_id"): str,
    },
)
@websocket_api.async_response
def api_get_entity_info(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Returns Music Assistant player information on a given player."""
    LOGGER.debug(f"Got message: {msg}")
    entity_id = msg["entity_id"]
    result = get_entity_info(hass, entity_id)
    LOGGER.debug(f"Sending result {result}")
    connection.send_result(msg["id"], result)


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


@websocket_api.websocket_command(
    {
        vol.Required("type"): "mass_queue/encode_images",
        vol.Required("entity_id"): str,
        vol.Required("images"): list,
    },
)
@websocket_api.async_response
async def api_download_images(
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
        img = await download_single_image_from_image_data(
            image,
            entity_id,
            hass,
            session,
        )
        image["encoded"] = img
        result.append(image)
    connection.send_result(msg["id"], result)
