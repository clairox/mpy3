"""
This module contains important enums
"""

from enum import Enum

from vlc import EventType, Meta, State


class VLCEventType:
    """
    VLC Events
    """

    MEDIA_STATE_CHANGED = EventType(5)
    MEDIA_PLAYER_TIME_CHANGED = EventType(267)


class MediaState:
    """
    Media playback state
    """

    ENDED = State(6)


class PlaybackMode(Enum):
    """
    Playback modes
    """

    DEFAULT = 0
    LOOP = 1
    REPEAT = 2


class MediaMeta:
    """
    Media metadata
    """

    TITLE = Meta(0)
    ARTIST = Meta(1)
