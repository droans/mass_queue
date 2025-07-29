<!-- [![HACS Default][hacs_shield]][hacs] -->
[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]
[![Installations][installations_shield]][releases]

# Music Assistant Queue Actions

Adds new actions to control player queues for Music Assistant 

## New actions:

---
`mass_queue.get_queue_items`: Returns the items (songs, podcast episods, etc.) within a queue

| Parameter | Type | Required | Default                     | Description                                                                                                                                                      |
|-----------|------|----------|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `entity`  | str  | Yes      | n/a                         | Music assistant player entity                                                                                                                                    |
| `limit`   | int  | No       | 500                         | Number of items in queue to return                                                                                                                               |
| `offset`  | int  | No       | <Current Item Position> - 5 | Location in queue to start where zero equals the first item in queue, not the current item. By default, will start with five items before actively playing item. |

`mass_queue.remove_queue_item`: Removes an item out of the queue

| Parameter       | Type | Required | Default | Description                                    |
|-----------------|------|----------|---------|------------------------------------------------|
| `entity`        | str  | Yes      | n/a     | Music assistant player entity                  |
| `queue_item_id` | str  | Yes      | n/a     | The `queue_item_id` of the corresponding item. |

`mass_queue.play_queue_item`: Plays the given item for the queue

| Parameter       | Type | Required | Default | Description                                    |
|-----------------|------|----------|---------|------------------------------------------------|
| `entity`        | str  | Yes      | n/a     | Music assistant player entity                  |
| `queue_item_id` | str  | Yes      | n/a     | The `queue_item_id` of the corresponding item. |

`mass_queue.move_queue_item_up`: Move an item in the queue up one position

| Parameter       | Type | Required | Default | Description                                    |
|-----------------|------|----------|---------|------------------------------------------------|
| `entity`        | str  | Yes      | n/a     | Music assistant player entity                  |
| `queue_item_id` | str  | Yes      | n/a     | The `queue_item_id` of the corresponding item. |

`mass_queue.move_queue_item_down`: Move an item in the queue down one position

| Parameter       | Type | Required | Default | Description                                    |
|-----------------|------|----------|---------|------------------------------------------------|
| `entity`        | str  | Yes      | n/a     | Music assistant player entity                  |
| `queue_item_id` | str  | Yes      | n/a     | The `queue_item_id` of the corresponding item. |

`mass_queue.move_queue_item_next`: Move an item to the next slot in the queue

| Parameter       | Type | Required | Default | Description                                    |
|-----------------|------|----------|---------|------------------------------------------------|
| `entity`        | str  | Yes      | n/a     | Music assistant player entity                  |
| `queue_item_id` | str  | Yes      | n/a     | The `queue_item_id` of the corresponding item. |
