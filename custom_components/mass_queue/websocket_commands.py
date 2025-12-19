"""Music Assistant Queue Actions Websocket Commands."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

import voluptuous as vol
from aiohttp import web
from aiohttp.hdrs import CACHE_CONTROL
from homeassistant.components import websocket_api
from homeassistant.components.http import KEY_HASS, HomeAssistantView
from homeassistant.components.media_player import async_fetch_image
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client

if TYPE_CHECKING:
    from aiohttp.typedefs import LooseHeaders
    from homeassistant.core import HomeAssistant

from .const import LOGGER
from .utils import (
    download_and_encode_image,
    download_single_image_from_image_data,
    get_entity_info,
    get_mass_client,
    proxy_image,
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


@websocket_api.websocket_command(
    {
        vol.Required("type"): "mass_queue/proxy_image_urls",
        vol.Required("image_urls"): vol.Any(list[str], str),
    },
)
@websocket_api.async_response
async def api_proxy_image(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Download images and return them as b64 encoded."""
    LOGGER.debug(f"Received message: {msg}")
    images = msg["image_urls"]
    images = (
        "".join(images)
        if sum([len(image) for image in images]) == len(images)
        else images
    )
    LOGGER.debug(f"Pulled images from message: {images}")
    result = []
    for image in images:
        if image.startswith("/api/"):
            LOGGER.debug("URL is API, returning same image")
            content = image
            content_type = "url"
        else:
            LOGGER.debug("URL is not API, proxying image")
            content, content_type = await proxy_image(hass, image)
            LOGGER.debug(f"Got content type of {content_type} for {image}")
        result.append({"url": image, "content": content, "content_type": content_type})
    connection.send_result(msg["id"], result)


class ApiFakeView(HomeAssistantView):
    """Fake API Endpoint for testing."""

    url = "/api/fake"
    name = "api:fake"

    @callback
    def get(self, request: web.Request) -> web.Response:
        """Returns a default response."""
        LOGGER.exception(request.app)
        return self.json_message("Hello!")


class ApiFakeView2(HomeAssistantView):
    """Fake API Endpoint for testing with templating."""

    url = "/api/fake2/{dummy}"
    name = "api:fake2"

    @callback
    def get(self, request: web.Request, dummy: str) -> web.Response:  # noqa: ARG002
        """Returns a default response with provided string."""
        LOGGER.exception(dummy)
        return self.json_message(f"Hello {dummy}!")


class ApiMassQueueProxyByEntityAndIdView(HomeAssistantView):
    """Endpoint to proxy Music Assistant images."""

    url = "/api/mass_queue/image_proxy/by_id/{player_entity_id}/{media_id}"
    name = "api:mass_queue:image:by_id"

    async def get(
        self,
        request: web.Request,
        player_entity_id: str,
        media_id: str,
    ) -> web.Response:
        """Returns a proxied image by ID."""
        LOGGER.debug(f"Got request for media id {media_id}")
        hass = request.app()[KEY_HASS]
        LOGGER.debug(f"Got Hass {hass}")
        client = get_mass_client(hass, player_entity_id)
        LOGGER.debug(f"Got client {client}")
        media_item = await client.music.get_item_by_uri(media_id)
        LOGGER.debug(f"Got media item {media_item}")
        image = client.music.get_media_item_image(media_item)
        image_path = image.path
        LOGGER.debug(f"Got image {image_path} ({image}), getting proxy data...")
        data, content_type = await async_fetch_image(LOGGER, hass, image_path)
        enc = f"data:{content_type};base64,{base64.b64encode(data).decode('utf-8')}"
        LOGGER.debug(f"Got content type {content_type} (content: {type(data)})")
        headers: LooseHeaders = {CACHE_CONTROL: "max-age=3600"}
        LOGGER.debug(f"Sending back response with headers {headers}")
        try:
            resp = web.Response(body=enc, content_type=content_type, headers=headers)
            LOGGER.debug("Response:")
            LOGGER.debug(resp)
        except Exception as e:
            LOGGER.debug(f"Got error: {e}")
            raise e  # noqa: TRY201
        else:
            return resp


class ApiMassQueueProxyImageURL(HomeAssistantView):
    """Endpoint to proxy Music Assistant images."""

    url = "/api/mass_queue/image_proxy/by_id/{player_entity_id}/{media_id}"
    name = "api:mass_queue:image:by_id"

    @callback
    def get(
        self,
        request: web.Request,
        player_entity_id: str,
        media_id: str,
    ) -> web.Response:
        """Returns a proxied image by ID."""
        hass = request.app()[KEY_HASS]
        client = get_mass_client(hass, player_entity_id)
        media_item = client.music.get_item_by_uri(media_id)
        image = client.music.get_media_item_image(media_item)
        data, content_type = proxy_image(image.path)
        headers: LooseHeaders = {CACHE_CONTROL: "max-age=3600"}
        return web.Response(body=data, content_type=content_type, headers=headers)
