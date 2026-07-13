# ty:ignore[unresolved-import]
"""API endpoint to serve media images."""
from functools import lru_cache

from aiohttp import web
from homeassistant.components.http import KEY_AUTHENTICATED, HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .const import LOGGER
from .utils import validate_access_token


class MediaImageView(HomeAssistantView):
    """API to Return media images."""

    requires_auth = False
    url = "/api/mass_queue_proxy/{entity_id}/{image_url}"
    name = "api:mass_queue:image"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize view."""
        LOGGER.info("Initializing mass queue proxy.")
        self.hass = hass

    @lru_cache(maxsize=512)  # noqa: B019
    async def download_image(self, url: str):
        """Download a single image without encoding it."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        return await session.get(url)

    def validate_token(self, entity_id: str, token: str) -> bool:
        """Check if token is valid."""
        return validate_access_token(self.hass, entity_id, token)

    async def get(
        self,
        request: web.Request,
        entity_id: str,
        image_url: str,
    ) -> web.StreamResponse:
        """Start a request."""
        token = request.query.get("token")
        authenticated = request[KEY_AUTHENTICATED] or self.validate_token(
            entity_id,
            token,
        )
        if not authenticated:
            raise web.HTTPUnauthorized
        LOGGER.error(f"Got request to proxy image for URL {image_url}")
        image = await self.download_image(image_url)
        content_type = image.content_type
        content_len = image.headers.get("Content-Length")
        if not content_len:
            content_len = image.content.total_bytes
        return web.Response(
            content_type=content_type,
            body=image.content,
            headers={"Content-Length": str(content_len)},
        )
