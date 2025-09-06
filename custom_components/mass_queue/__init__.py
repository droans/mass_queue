"""Initialize component."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_URL, EVENT_HOMEASSISTANT_STOP
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)
from music_assistant_client import MusicAssistantClient
from music_assistant_client.exceptions import CannotConnect, InvalidServerVersion
from music_assistant_models.errors import ActionUnavailable, MusicAssistantError

from .actions import (
    MassQueueActions,
    get_music_assistant_client,
    setup_controller_and_actions,
)
from .const import DOMAIN, LOGGER
from .services import register_actions

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType, Event

PLATFORMS = []

CONNECT_TIMEOUT = 10
LISTEN_READY_TIMEOUT = 30

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type MusicAssistantConfigEntry = ConfigEntry[MusicAssistantQueueEntryData]


@dataclass
class MusicAssistantQueueEntryData:
    """Hold Mass data for the config entry."""

    mass: MusicAssistantClient
    actions: MassQueueActions
    listen_task: asyncio.Task


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # noqa: ARG001
    """Set up the Music Assistant component."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MusicAssistantConfigEntry,
) -> bool:
    """Set up Music Assistant from a config entry."""
    http_session = async_get_clientsession(hass, verify_ssl=False)
    mass_url = entry.data[CONF_URL]
    mass = MusicAssistantClient(mass_url, http_session)

    try:
        async with asyncio.timeout(CONNECT_TIMEOUT):
            await mass.connect()
    except (TimeoutError, CannotConnect) as err:
        exc = f"Failed to connect to music assistant server {mass_url}"
        raise ConfigEntryNotReady(
            exc,
        ) from err
    except InvalidServerVersion as err:
        async_create_issue(
            hass,
            DOMAIN,
            "invalid_server_version",
            is_fixable=False,
            severity=IssueSeverity.ERROR,
            translation_key="invalid_server_version",
        )
        exc = f"Invalid server version: {err}"
        raise ConfigEntryNotReady(exc) from err
    except MusicAssistantError as err:
        LOGGER.exception("Failed to connect to music assistant server", exc_info=err)
        exc = f"Unknown error connecting to the Music Assistant server {mass_url}"
        raise ConfigEntryNotReady(
            exc,
        ) from err

    async_delete_issue(hass, DOMAIN, "invalid_server_version")

    async def on_hass_stop(event: Event) -> None:  # noqa: ARG001
        """Handle incoming stop event from Home Assistant."""
        await mass.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop),
    )

    # launch the music assistant client listen task in the background
    # use the init_ready event to wait until initialization is done
    init_ready = asyncio.Event()
    listen_task = asyncio.create_task(_client_listen(hass, entry, mass, init_ready))

    try:
        async with asyncio.timeout(LISTEN_READY_TIMEOUT):
            await init_ready.wait()
    except TimeoutError as err:
        listen_task.cancel()
        exc = "Music Assistant client not ready"
        raise ConfigEntryNotReady(exc) from err

    # store the listen task and mass client in the entry data
    actions = await setup_controller_and_actions(hass, mass)
    register_actions(hass)
    entry.runtime_data = MusicAssistantQueueEntryData(mass, actions, listen_task)

    # If the listen task is already failed, we need to raise ConfigEntryNotReady
    if listen_task.done() and (listen_error := listen_task.exception()) is not None:
        await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        try:
            await mass.disconnect()
        finally:
            raise ConfigEntryNotReady(listen_error) from listen_error

    # initialize platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _client_listen(
    hass: HomeAssistant,
    entry: ConfigEntry,
    mass: MusicAssistantClient,
    init_ready: asyncio.Event,
) -> None:
    """Listen with the client."""
    try:
        await mass.start_listening(init_ready)
    except MusicAssistantError as err:
        if entry.state != ConfigEntryState.LOADED:
            raise
        LOGGER.error("Failed to listen: %s", err)
    except Exception as err:  # pylint: disable=broad-except
        # We need to guard against unknown exceptions to not crash this task.
        if entry.state != ConfigEntryState.LOADED:
            raise
        LOGGER.exception("Unexpected exception: %s", err)

    if not hass.is_stopping:
        LOGGER.debug("Disconnected from server. Reloading integration")
        hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        mass_entry_data: MusicAssistantQueueEntryData = entry.runtime_data
        mass_entry_data.listen_task.cancel()
        await mass_entry_data.mass.disconnect()

    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Remove a config entry from a device."""
    player_id = next(
        (
            identifier[1]
            for identifier in device_entry.identifiers
            if identifier[0] == DOMAIN
        ),
        None,
    )
    if player_id is None:
        # this should not be possible at all, but guard it anyways
        return False
    mass = get_music_assistant_client(hass, config_entry.entry_id)
    if mass.players.get(player_id) is None:
        # player is already removed on the server, this is an orphaned device
        return True
    # try to remove the player from the server
    try:
        await mass.config.remove_player_config(player_id)
    except ActionUnavailable:
        return False
    else:
        return True
