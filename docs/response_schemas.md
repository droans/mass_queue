# Schemas

## Service Schemas

### GetQueueItemsResponseSchema

```yaml
[player_name: str]: QueueItemSchema[]
```

### GetGroupVolumeResponseSchema

```yaml
volume_level: int
```


### SendCommandResponseSchema

```yaml
response: any
```

### GetRecommendationsResponseSchema

```yaml
response: RecommendationFolder[]
```

### GetAlbumResponseSchema

*See [music_assistant_models.media_items.Album](https://github.com/music-assistant/models/blob/0f2ad708ab26d2cc2ae008872afc00cd4a795380/music_assistant_models/media_items/media_item.py#L208)*


### GetArtistResponseSchema

*See [music_assistant_models.media_items.Artist](https://github.com/music-assistant/models/blob/0f2ad708ab26d2cc2ae008872afc00cd4a795380/music_assistant_models/media_items/media_item.py#L198)*

### GetPlaylistResponseSchema

*See [music_assistant_models.media_items.Playlist](https://github.com/music-assistant/models/blob/0f2ad708ab26d2cc2ae008872afc00cd4a795380/music_assistant_models/media_items/media_item.py#L254)*

### GetPodcastResponseSchema

*See [music_assistant_models.media_items.Podcast](https://github.com/music-assistant/models/blob/0f2ad708ab26d2cc2ae008872afc00cd4a795380/music_assistant_models/media_items/media_item.py#L323)*

### GetAlbumTracksResponseSchema

```yaml
tracks: TrackSchame[]
```

### GetArtistTracksResponseSchema

```yaml
tracks: TrackSchame[]
```

### GetPlaylistTracksResponseSchema

```yaml
tracks: PlaylistTrackSchema[]
```

### GetPodcastEpisodesResponseSchema

```yaml
episodes: PodcastEpisodeSchema[]
```

## WebSocket Schemas

### GetInfoResponseSchema

```yaml
available: bool
can_group_with: str[]       # List of player IDs that can be natively synced using `media_player.join`
connection:
  configuration_url: str    # URL to configure the player from Music Assistant
  url: str                  # IP Address for player
entries:                    # Config Entry IDs for the player's HA integrations
  music_assistant: str
  mass_queue: str
features: str[]             # List of features which the player supports
manufacturer: str
model: str
name: str
player_id: str              # ID of player in Music Assistant
provider: str
queue_id: str               # ID for queue currently playing on player
server:
  connection:
    url: str                # URL to access Music Assistant integration
    websocket: str          # WebSocket address to interact with player
synced_to: str| None        # Player(s) which are currently synced/grouped/joined with the player
type: str
```

### GetUser
*See [music_assistant_models.auth.User](https://github.com/music-assistant/models/blob/0f2ad708ab26d2cc2ae008872afc00cd4a795380/music_assistant_models/auth.py#L29)*


### DownloadAndEncodeImageResponseSchema

```yaml
<Base64 encoded string representation of image>
```

## Sub-schemas

### QueueItemSchema

```yaml
queue_item_id: str
media_title: str
media_album_name: str
media_artist: str
media_content_id: str
media_image: str
favorite: bool
```

### TrackSchema

```yaml
media_title: str
media_content_id: str
duration?: int
media_image: str
local_image_encoded?: str
favorite: bool
media_album_name: str
media_artist: str
```

### PlaylistTrackSchema

```yaml
media_title: str
media_content_id: str
duration?: int
media_image: str
local_image_encoded?: str
favorite: bool
media_album_name: str
media_artist: str
position: int
```

### PodcastEpisodeSchema

```yaml
media_title: str
media_content_id: str
duration?: int
media_image: str
local_image_encoded?: str
favorite: bool
media_album_name: str
media_artist: str
release_date: str
```

*Note: release date is a string representation of a date, formatted as `YYYY-MM-DDTHH:MM:SS`.*

### RecommendationFolder

*See [music_assistant_models.media_items.RecommendationFolder](https://github.com/music-assistant/models/blob/0f2ad708ab26d2cc2ae008872afc00cd4a795380/music_assistant_models/media_items/media_item.py#L389)*
