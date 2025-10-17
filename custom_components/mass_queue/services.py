"""Service actions for mass_queue."""

from __future__ import annotations

from homeassistant.core import (
    ServiceCall,
    SupportsResponse,
    callback,
)

from .const import (
    ATTR_CONFIG_ENTRY_ID,
    ATTR_PLAYER_ENTITY,
    DOMAIN,
    SERVICE_GET_GROUP_VOLUME,
    SERVICE_GET_QUEUE_ITEMS,
    SERVICE_GET_RECOMMENDATIONS,
    SERVICE_MOVE_QUEUE_ITEM_DOWN,
    SERVICE_MOVE_QUEUE_ITEM_NEXT,
    SERVICE_MOVE_QUEUE_ITEM_UP,
    SERVICE_PLAY_QUEUE_ITEM,
    SERVICE_REMOVE_QUEUE_ITEM,
    SERVICE_SEND_COMMAND,
    SERVICE_SET_GROUP_VOLUME,
    SERVICE_UNFAVORITE_CURRENT_ITEM,
)
from .schemas import (
    GET_GROUP_VOLUME_SERVICE_SCHEMA,
    GET_RECOMMENDATIONS_SERVICE_SCHEMA,
    MOVE_QUEUE_ITEM_DOWN_SERVICE_SCHEMA,
    MOVE_QUEUE_ITEM_NEXT_SERVICE_SCHEMA,
    MOVE_QUEUE_ITEM_UP_SERVICE_SCHEMA,
    PLAY_QUEUE_ITEM_SERVICE_SCHEMA,
    QUEUE_ITEMS_SERVICE_SCHEMA,
    REMOVE_QUEUE_ITEM_SERVICE_SCHEMA,
    SEND_COMMAND_SERVICE_SCHEMA,
    SET_GROUP_VOLUME_SERVICE_SCHEMA,
    UNFAVORITE_CURRENT_ITEM_SERVICE_SCHEMA,
)
from .utils import get_entity_actions_controller, process_recommendations


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
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_RECOMMENDATIONS,
        get_recommendations,
        schema=GET_RECOMMENDATIONS_SERVICE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_GROUP_VOLUME,
        get_group_volume,
        schema=GET_GROUP_VOLUME_SERVICE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_GROUP_VOLUME,
        set_group_volume,
        schema=SET_GROUP_VOLUME_SERVICE_SCHEMA,
        supports_response=SupportsResponse.NONE,
    )


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


async def get_recommendations(call: ServiceCall):
    """Service wrapper to get recommendations from providers."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    result = await actions.get_recommendations(call)
    return {"response": process_recommendations(result)}


async def get_group_volume(call: ServiceCall):
    """Service wrapper to get grouped volume."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    result = await actions.get_group_volume(call)
    return {"volume_level": result}


async def set_group_volume(call: ServiceCall):
    """Service wrapper to set grouped volume."""
    entity_id = call.data[ATTR_PLAYER_ENTITY]
    hass = call.hass
    actions = get_entity_actions_controller(hass, entity_id)
    await actions.set_group_volume(call)
