"""Service actions for mass_queue."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er

from .const import (
    ATTR_CONFIG_ENTRY_ID,
    ATTR_PLAYER_ENTITY,
    DOMAIN,
    SERVICE_GET_QUEUE_ITEMS,
    SERVICE_MOVE_QUEUE_ITEM_DOWN,
    SERVICE_MOVE_QUEUE_ITEM_NEXT,
    SERVICE_MOVE_QUEUE_ITEM_UP,
    SERVICE_PLAY_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SERVICE_SEND_COMMAND,
    SERVICE_UNFAVORITE_CURRENT_ITEM,
)
from .schemas import (
    MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA,
    MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA,
    MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA,
    PLAY_QUEUE_ITEM_SERVICE_SCHEMA,
    QUEUE_ITEMS_SERVICE_SCHEMA,
    REMOVE_QUEUE_ITEM_SERVICE_SCHEMA,
    SEND_COMMAND_SERVICE_SCHEMA,
    UNFAVORITE_CURRENT_ITEM_SERVICE_SCHEMA,
)

if TYPE_CHECKING:
    from music_assistant_client import MusicAssistantClient

    from . import MassQueueEntryData


@callback
def register_actions(hass) -> None:
    """Registers actions with Home Assistant."""
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_QUEUE_ITEMS,
        get_queue_items,
        schema=QUEUE_ITEMS_SERVICE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_MOVE_QUEUE_ITEM_DOWN,
        move_queue_item_down,
        schema=MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA,
        supports_response=SupportsResponse.NONE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_MOVE_QUEUE_ITEM_NEXT,
        move_queue_item_next,
        schema=MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA,
        supports_response=SupportsResponse.NONE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_MOVE_QUEUE_ITEM_UP,
        move_queue_item_up,
        schema=MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA,
        supports_response=SupportsResponse.NONE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY_QUEUE_ITEM,
        play_queue_item,
        schema=PLAY_QUEUE_ITEM_SERVICE_SCHEMA,
        supports_response=SupportsResponse.NONE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_QUEUE_ITEM,
        remove_queue_item,
        schema=REMOVE_QUEUE_ITEM_SERVICE_SCHEMA,
        supports_response=SupportsResponse.NONE,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_COMMAND,
        send_command,
        schema=SEND_COMMAND_SERVICE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UNFAVORITE_CURRENT_ITEM,
        unfavorite_current_item,
        schema=UNFAVORITE_CURRENT_ITEM_SERVICE_SCHEMA,
        supports_response=SupportsResponse.NONE,
    )


def _get_mass_entity_config_entry_id(hass, entity_id):
    """Helper to grab config entry ID from entity ID."""
    registry = er.async_get(hass)
    return registry.async_get(entity_id).config_entry_id


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


def get_mass_entry(hass, entity_id):
    """Helper function to pull MA Config Entry."""
    config_id = _get_mass_entity_config_entry_id(hass, entity_id)
    return _get_config_entry(hass, config_id)


def _get_mass_queue_entries(hass):
    """Gets all entries for mass_queue domain."""
    entries = hass.config_entries.async_entries()
    return [entry for entry in entries if entry.domain == "mass_queue"]


def find_mass_queue_entry(hass, mass_url):
    """Finds the mass_queue entry for the given MA URL."""
    entries = _get_mass_queue_entries(hass)
    for entry in entries:
        entry_url = entry.runtime_data.mass.connection.ws_server_url
        if entry_url == mass_url:
            return entry
    msg = f"Cannot find entry for Music Assistant at {mass_url}"
    raise ServiceValidationError(msg)


def get_entity_actions_controller(hass, entity_id):
    """Gets the actions for the selected entity."""
    mass_entry = get_mass_entry(hass, entity_id)
    mass = mass_entry.runtime_data.mass.connection.ws_server_url
    mass_queue_entry = find_mass_queue_entry(hass, mass)
    return mass_queue_entry.runtime_data.actions


async def get_queue_items(call: ServiceCall):
    """Service wrapper to get queue items."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    return await actions.get_queue_items(call)


async def move_queue_item_down(call: ServiceCall):
    """Service wrapper to move queue item down."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    return await actions.move_queue_item_down(call)


async def move_queue_item_next(call: ServiceCall):
    """Service wrapper to move queue item next."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    return await actions.move_queue_item_next(call)


async def move_queue_item_up(call: ServiceCall):
    """Service wrapper to move queue item up."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    return await actions.move_queue_item_up(call)


async def play_queue_item(call: ServiceCall):
    """Service wrapper to play a queue item."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    return await actions.play_queue_item(call)


async def remove_queue_item(call: ServiceCall):
    """Service wrapper to remove a queue item."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    return await actions.remove_queue_item(call)


async def send_command(call: ServiceCall):
    """Service wrapper to send command to Music Assistant."""
    entry_id = call.data[ATTR_CONFIG_ENTRY_ID]
    hass = call.hass
    entry = hass.config_entries.async_get_entry(entry_id)
    actions = entry.runtime_data.actions
    return await actions.send_command(call)


async def unfavorite_current_item(call: ServiceCall):
    """Service wrapper to unfavorite currently playing item."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    await actions.unfavorite_item(call)
