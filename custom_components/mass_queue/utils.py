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

def return_image_or_none(img_data: dict):
    """Returns None if image is not present or not remotely accessible."""
    if type(img_data) is dict:
        img = img_data.get("path")
        remote = img_data.get("remotely_accessible")
        if remote:
            return img
    return None

def search_image_list(images: list):
    """Checks through a list of image data and attempts to find an image."""
    result = None
    for item in images:
        image = return_image_or_none(item)
        if image is not None:
            result = image
            break
    return result

def find_image_from_image(data: dict):
    """Attempts to find the image via the image key."""
    img_data = data.get("image")
    return return_image_or_none(img_data)

def find_image_from_metadata(data: dict):
    """Attempts to find the image via the metadata key."""
    media_item = data.get("media_item", {})
    metadata = media_item.get("metadata", {})
    img_data = metadata.get("images")
    if img_data is None:
        return None
    return search_image_list(img_data)

def find_image_from_album(data: dict):
    """Attempts to find the image via the album key."""
    album = data.get("album", {})
    metadata = album.get("metadata", {})
    img_data = metadata.get("images")
    if img_data is None:
        return None
    return search_image_list(img_data)

def find_image_from_artists(data: dict):
    """Attempts to find the image via the artists key."""
    artist = data.get("artist", {})
    img_data = artist.get("image")
    if img_data is list:
        return search_image_list(img_data)
    return return_image_or_none(img_data)


def find_image(data: dict):
    """Returns None if image is not present or not remotely accessible."""
    from_image = find_image_from_image(data)
    from_metadata = find_image_from_metadata(data)
    from_album = find_image_from_album(data)
    from_artists = find_image_from_artists(data)
    return from_image or from_metadata or from_album or from_artists
