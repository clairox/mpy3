from vlc import EventType, Meta, PlaybackMode, State

SEEK_INTERVAL = 5000
ALLOWED_FILE_TYPES = [".mp3"]

# vlc.EventTypes
MEDIA_STATE_CHANGED_EVENT_TYPE = EventType(5)
MEDIA_PLAYER_MEDIA_CHANGED_EVENT_TYPE = EventType(0x100)
MEDIA_PLAYER_TIME_CHANGED = EventType(267)

# vlc.States
IDLE_STATE = State(0)
PLAYING_STATE = State(3)
PAUSED_STATE = State(4)
STOPPING_STATE = State(5)
ENDED_STATE = State(6)

# vlc.PlaybackModes
DEFAULT_PB_MODE = PlaybackMode(0)
LOOP_PB_MODE = PlaybackMode(1)
REPEAT_PB_MODE = PlaybackMode(2)


# vlc.Metas
TITLE_META = Meta(0)
ARTIST_META = Meta(1)
