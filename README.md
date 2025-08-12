[![GitHub Release](https://img.shields.io/github/release/droans/mass_queue.svg?style=for-the-badge)](https://github.com/droans/mass_card/releases)
[![License](https://img.shields.io/github/license/droans/mass_queue.svg?style=for-the-badge)](LICENSE)
[![Project Maintenance](https://img.shields.io/badge/maintainer-droans-blue.svg?style=for-the-badge)](https://github.com/droans)
[![GitHub Activity](https://img.shields.io/github/last-commit/droans/mass_queue?style=for-the-badge)](https://github.com/droans/mass_card/commits/main)

# Music Assistant Queue Actions

Adds new actions to control player queues for Music Assistant 

## New actions:

---
`mass_queue.get_queue_items`: Returns the items (songs, podcast episods, etc.) within a queue

| Parameter | Type | Required | Default                     | Description                                                                                                                                                      |
|-----------|------|----------|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `entity`        | str  | Yes      | n/a                         | Music assistant player entity                                                                                                                                    |
| `limit`         | int  | No       | 500                         | Number of items in queue to return                                                                                                                               |
| `offset`        | int  | No       | <Current Item Position> - 5 | Location in queue to start where zero equals the first item in queue, not the current item. By default, will start with five items before actively playing item. |
| `limit_before`  | int  | No       | n/a                         | Number of items to pull before current active item in queue.                                                                                                     |
| `limit_after`   | int  | No       | n/a                         | Number of items to pull after current active item in queue.                                                                                                      |

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


## Installation

1. Add this to your HACS repositories.
    * In Home Assistant, navigate to your HACS dashboard
    * In the upper-right corner, select the three-dot overflow button and click "Custom Repositories".
    * For the "Repository", type in `https://github.com/droans/mass_queue`. 
    * For the "Type", select "Integration"
    * Click "Add"
2. Search for "Music Assistant Queue Actions" in HACS. 
3. Select the repository and install. 

## Configuration

The integration should automatically detect the active Music Assistant instance and integration. If it does not, add as you normally would from the "Devices & Services" section in the Home Assistant Settings.