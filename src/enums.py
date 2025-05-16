"""
This module contains important enums
"""

from enum import Enum

from vlc import EventType, Meta, State


class Control(Enum):
    """
    Enum representing application commands
    """

    NONE = 0
    PLAY = 1
    FFORWARD = 2
    REWIND = 3
    NEXT = 4
    BACK = 5
    QUIT = 6
    STOP = 7
    TOGGLE_MODE = 8
    TOGGLE_SHUFFLE = 9


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
