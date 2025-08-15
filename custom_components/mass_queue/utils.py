"""Utilities."""


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
