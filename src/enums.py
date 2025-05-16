"""
This module contains important enums
"""

from enum import Enum

import vlc


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


class VLCEvent:
    """
    VLC Events
    """

    MEDIA_STATE_CHANGED = vlc.EventType(5)
    MEDIA_PLAYER_TIME_CHANGED = vlc.EventType(267)


class MediaState:
    """
    Media playback state
    """

    ENDED = vlc.State(6)


class PlaybackMode(Enum):
    """
    Playback modes
    """

    DEFAULT = 0
    LOOP = 1
    REPEAT = 2


class MediaMetadata:
    """
    Media metadata
    """

    TITLE = vlc.Meta(0)
    ARTIST = vlc.Meta(1)
