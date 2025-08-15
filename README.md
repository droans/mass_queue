<div align="center">

[![GitHub Release][release-shield]][release]
[![Beta][beta-shield]][beta]
[![HACS][hacs-badge-shield]][hacs-badge]

[![Maintainer][maintainer-shield]][maintainer]
[![GitHub Activity][activity-shield]][activity]
[![License][license-shield]][license]

</div>

[release-shield]: https://img.shields.io/github/release/droans/mass_queue.svg?style=for-the-badge
[release]: https://github.com/droans/mass_queue/releases
[license-shield]: https://img.shields.io/github/license/droans/mass_queue.svg?style=for-the-badge
[license]: LICENSE
[hacs-badge-shield]: https://img.shields.io/badge/HACS-Default-blue.svg?style=for-the-badge
[hacs-badge]: https://github.com/hacs/default
[maintainer-shield]: https://img.shields.io/badge/maintainer-droans-blue.svg?style=for-the-badge
[maintainer]: https://github.com/droans
[activity-shield]: https://img.shields.io/github/last-commit/droans/mass_queue?style=for-the-badge
[activity]: https://github.com/droans/mass_card/commits/main
[beta-shield]: https://img.shields.io/github/v/release/droans/mass_queue?include_prereleases&style=for-the-badge&filter=*b*&label=Pre-Release
[beta]: https://github.com/droans/mass_queue/releases

# Music Assistant Queue Actions

Adds new actions to control player queues for Music Assistant

Designed to work with [Music Assistant Queue Card](https://github.com/droans/mass_card)

[![My Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=mass_queue&owner=droans&category=Integration)

## New actions:

---
`mass_queue.get_queue_items`: Returns the items (songs, podcast episods, etc.) within a queue

| Parameter | Type | Required | Default                           | Description                                                                                                                                                      |
|-----------|------|----------|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `entity`        | str  | Yes      | n/a                         | Music assistant player entity                                                                                                                                    |
| `limit`         | int  | No       | 500                         | Number of items in queue to return                                                                                                                               |
| `offset`        | int  | No       | n/a                         | Location in queue to start where zero equals the first item in queue, not the current item. By default, will start with five items before actively playing item. |
| `limit_before`  | int  | No       | 5                           | Number of items to pull before current active item in queue.                                                                                                     |
| `limit_after`   | int  | No       | 100                         | Number of items to pull after current active item in queue.                                                                                                      |

Example Output:
```yaml
media_player.music_assistant_speaker:
  - queue_item_id: f62a98bb794447e28e8400367cf0b68a
    media_title: Summer Friends (feat. Jeremih & Francis & The Lights)
    media_album_name: Coloring Book
    media_artist: Chance the Rapper, Jeremih, Francis and the Lights
    media_content_id: tidal://track/60920018
    media_image: https://resources.tidal.com/images/1d765014/8be5/4f60/a657/bce7eee1ef8b/750x750.jpg
  - queue_item_id: a6272438f57843808d891c59fec4c8bf
    media_title: Fireflies
    media_album_name: Ocean Eyes
    media_artist: Owl City
    media_content_id: tidal://track/3140991
    media_image: https://resources.tidal.com/images/76b92beb/399c/4983/9b91/0eef89c796e1/750x750.jpg
  ...
```

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

1. Download and install the integration by using the button above.

## Configuration

The integration should automatically detect the active Music Assistant instance and integration. If it does not, add as you normally would from the "Devices & Services" section in the Home Assistant Settings.
