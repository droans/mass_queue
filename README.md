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

Designed to work with [Music Assistant Player Card](https://github.com/droans/mass-player-card)

[![My Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=mass_queue&owner=droans&category=Integration)

## New actions:

---

<details>
<summary>Queue Actions</summary>

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

`mass_queue.send_command`: Sends a command to the Music Assistant API and returns the response. You may find the various commands by searching for `@api_command` in the [music_assistant/server](http://github.com/music-assistant/server/) repository.

| Parameter         | Type | Required | Default | Description                                 |
|-------------------|------|----------|---------|---------------------------------------------|
| `command`         | str  | Yes      | n/a     | The command to send to Music Assistant      |
| `data`            | dict | No       | None    | Any data to send with the command           |
| `config_entry_id` | dict | No       | None    | The ID of the used `mass_queue` integration |

`mass_queue.clear_queue_from_here`: Clear the items in a queue after the currently playing item.

| Parameter | Type | Required | Default | Description                   |
|-----------|------|----------|---------|-------------------------------|
| `entity`  | str  | Yes      | n/a     | Music assistant player entity |

`mass_queue.unfavorite_current_item`: Unfavorite the currently playing item

| Parameter | Type | Required | Default | Description                   |
|-----------|------|----------|---------|-------------------------------|
| `entity`  | str  | Yes      | n/a     | Music assistant player entity |

</summary>

<details>
<summary>Group Actions</summary>

`mass_queue.set_group_volume`: Sets the volume for the group which the provided player belongs to.

| Parameter | Type | Required | Default | Description                   |
|-----------|------|----------|---------|-------------------------------|
| `entity`  | str  | Yes      | n/a     | Music assistant player entity |

`mass_queue.get_group_volume`: Returns the volume for a player group.

| Parameter | Type | Required | Default | Description                   |
|-----------|------|----------|---------|-------------------------------|
| `entity`  | str  | Yes      | n/a     | Music assistant player entity |

</summary>

<details>
<summary>Collection Actions</summary>

`mass_queue.get_recommendations`: Get recommendations from your music providers.

| Parameter    | Type        | Required | Default | Description                                        |
|--------------|-------------|----------|---------|----------------------------------------------------|
| `entity`     | str         | Yes      | n/a     | Music assistant player entity                      |
| `providers`  | list of str | No       | n/a     | Limit recommendations to the specified provider(s) |

---
### Albums
`mass_queue.get_album`: Returns information about an album from the MA server.

| Parameter         | Type | Required | Default | Description                                 |
|-------------------|------|----------|---------|---------------------------------------------|
| `config_entry_id` | str  | No       | None    | The ID of the used `mass_queue` integration |
| `uri`             | str  | Yes      | n/a     | The URI for the playlist                    |

`mass_queue.get_album_tracks`: Returns some or all tracks for the album given by the URI.

| Parameter         | Type | Required | Default | Description                                              |
|-------------------|------|----------|---------|----------------------------------------------------------|
| `config_entry_id` | str  | No       | None    | The ID of the used `mass_queue` integration              |
| `uri`             | str  | Yes      | n/a     | The URI for the album                                    |
| `page`            | int  | No       | None    | Page of results to return. If not provided, returns all. |

---
### Artists
`mass_queue.get_artist`: Returns information about an artist from the MA server.

| Parameter         | Type | Required | Default | Description                                 |
|-------------------|------|----------|---------|---------------------------------------------|
| `config_entry_id` | str  | No       | None    | The ID of the used `mass_queue` integration |
| `uri`             | str  | Yes      | n/a     | The URI for the playlist                    |

`mass_queue.get_artist_tracks`: Returns the top tracks for the artist given by the URI.

| Parameter         | Type | Required | Default | Description                                              |
|-------------------|------|----------|---------|----------------------------------------------------------|
| `config_entry_id` | str  | No       | None    | The ID of the used `mass_queue` integration              |
| `uri`             | str  | Yes      | n/a     | The URI for the artist                                   |
| `page`            | int  | No       | None    | Page of results to return. If not provided, returns all. |

---
### Playlists
`mass_queue.get_playlist`: Returns information about a playlist from the MA server.

| Parameter         | Type | Required | Default | Description                                 |
|-------------------|------|----------|---------|---------------------------------------------|
| `config_entry_id` | str  | No       | None    | The ID of the used `mass_queue` integration |
| `uri`             | str  | Yes      | n/a     | The URI for the playlist                    |

`mass_queue.get_playlist_tracks`: Returns some or all tracks for the playlist given by the URI.

| Parameter         | Type | Required | Default | Description                                              |
|-------------------|------|----------|---------|----------------------------------------------------------|
| `config_entry_id` | str  | No       | None    | The ID of the used `mass_queue` integration              |
| `uri`             | str  | Yes      | n/a     | The URI for the playlist                                 |
| `page`            | int  | No       | None    | Page of results to return. If not provided, returns all. |

`mass_queue.remove_playlist_tracks`: Removes one or more tracks from a playlist based on their position. **IMPORTANT: SEE WARNING BELOW**

| Parameter             | Type        | Required | Default | Description                                       |
|-----------------------|-------------|----------|---------|---------------------------------------------------|
| `config_entry_id`     | str         | Yes      | n/a     | The ID of the used `mass_queue` integration       |
| `playlist_id`         | str         | Yes      | n/a     | The ID of the playlist                            |
| `positions_to_remove` | list of str | Yes      | n/a     | Position(s) of items to remove from the playlist. |

### ⚠️WARNING: mass_queue.remove_playlist_tracks is bad for your health.⚠️

`mass_queue.remove_playlist_tracks` is **dangerous**.

Music Assistant will use the positions in a playlist to determine which tracks to remove. However, it does not provide an updated playlist immediately, instead waiting for the next refresh.

You must be **VERY** careful if you are using this action. You should **NOT** rely on proper feedback from Music Assistant. If you plan on using this, you MUST plan to work around this.

---

### Podcasts
`mass_queue.get_podcast`: Returns information about a podcast from the MA server.

| Parameter         | Type | Required | Default | Description                                 |
|-------------------|------|----------|---------|---------------------------------------------|
| `config_entry_id` | str  | No       | None    | The ID of the used `mass_queue` integration |
| `uri`             | str  | Yes      | n/a     | The URI for the playlist                    |

`mass_queue.get_podcast_episodes`: Returns some or all episodes for the podcast given by the URI.

| Parameter         | Type | Required | Default | Description                                              |
|-------------------|------|----------|---------|----------------------------------------------------------|
| `config_entry_id` | str  | No       | None    | The ID of the used `mass_queue` integration              |
| `uri`             | str  | Yes      | n/a     | The URI for the podcast                                  |
| `page`            | int  | No       | None    | Page of results to return. If not provided, returns all. |

</summary>

## Installation

1. Download and install the integration by using the button above.

## Configuration

The integration should automatically detect the active Music Assistant instance and integration. If it does not, add as you normally would from the "Devices & Services" section in the Home Assistant Settings.


# FAQs

## I use a local provider (eg, Filesystem, Plex, Jellyfin, etc) and my images aren't showing up! What gives?!

Local music providers are a bit different than cloud. When you are using Plex or Jellyfin, the image returned is an HTTP URL for their local IP address. This is problematic - most users access Home Assistant via HTTP**S** and modern browsers prohibit mixed content (insecure content on secure sites). For filesystem providers, it's even more difficult as Music Assistant returns their path on the filesystem instead of a URL.

However, there is a workaround!

You may enable the `download_local` option by navigating to the integration's listing in Home Assistant and selecting the cog next to the entry. When this is enabled, the integration will attempt to download and encode the image for any item which does not have any images marked as `remotely_accessible`.

This option will then return a new attribute for these queue items labeled `local_image_encoded`. Custom cards can then utilize this in their code in place of the image URL.

## I am the creator of a custom card. Can I use these actions in my own card, too?

Of course - this is open-source! The only requirement is that you give credit.

## I would like to sponsor you/the card and/or pay to add a new feature!

While I appreciate it, I am not going to accept any funding.

When someone funds development, there's often an implied belief that the card will keep being developed or the maintainer will provide new projects. I want to be able to drop development on this card when I feel that it is complete. I do not want people to feel misled, cheated, or that I should prioritize their wants over anything else. This card is something I created for myself

### WARNINGS

* This is not a cure-all and should not be enabled unless you need it.
* This will not have any effect unless any frontend card supports it.
* Loading the integration and updating the queue WILL take much longer. Each item must be downloaded and converted. This is NOT a quick process. Depending on your server, this may take between 2-20 seconds per item.
* This requires that Home Assistant can directly access the Music Assistant server along with the local provider.
