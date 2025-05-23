"""
This module handles playback status output to the console
"""

from enum import Enum

from enums import PlaybackMode
from utils import create_timestring, log


class PlaybackState(Enum):
    """
    Current playback state
    """

    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


class PlaybackStatusDisplay:
    """
    The media playback status to be displayed in the console

    Args:
        state (PlaybackState): Current playback state
        media_label (str): Basic information about selected media
        position (int): Current media playback time
        total_duration (int): Total duration of selected media
        shuffle (bool): Whether playback order is randomized
        playback_mode (PlaybackMode): Default, loop, or repeat
    """

    def __init__(self, **kwargs) -> None:
        self.state = PlaybackState.STOPPED
        self.media_label = "No track selected"
        self.position = -1
        self.total_duration = -1
        self.shuffle = False
        self.playback_mode = PlaybackMode.DEFAULT

        self.status = ""

        self.set_attrs(**kwargs)
        self.update_status_string(**kwargs)

    def set_attrs(self, **kwargs) -> None:
        """
        Sets the media playback status attributes
        """

        if "state" in kwargs:
            self.state = kwargs["state"]

        if "media_label" in kwargs:
            self.media_label = kwargs["media_label"]

        if "position" in kwargs:
            self.position = kwargs["position"]

        if "total_duration" in kwargs:
            self.total_duration = kwargs["total_duration"]

        if "shuffle" in kwargs:
            self.shuffle = kwargs["shuffle"]

        if "playback_mode" in kwargs:
            self.playback_mode = kwargs["playback_mode"]

    def update_status_string(self, **kwargs) -> None:
        """
        Update the status output string
        """

        self.set_attrs(**kwargs)

        state_display = ""
        if self.state == PlaybackState.STOPPED:
            state_display = "⏹ Stopped"
        elif self.state == PlaybackState.PLAYING:
            state_display = "▶ Playing"
        elif self.state == PlaybackState.PAUSED:
            state_display = "⏸ Paused"

        shuffle_display = ""
        if self.shuffle:
            shuffle_display = "Shuffle On"
        else:
            shuffle_display = "Shuffle Off"

        playback_mode_display = ""
        if self.playback_mode == PlaybackMode.DEFAULT:
            playback_mode_display = "Loop Off"
        elif self.playback_mode == PlaybackMode.LOOP:
            playback_mode_display = "Loop All"
        elif self.playback_mode == PlaybackMode.REPEAT:
            playback_mode_display = "Repeat 1"

        self.status = f"{state_display:<9}  |  {shuffle_display:<11}  |  {playback_mode_display:<7}  |  {self.media_label:<40}"

        if self.state != PlaybackState.STOPPED:
            self.status += (
                f"  |  {create_timestring(self.position, self.total_duration)}"
            )

    def update(self, **kwargs) -> None:
        """
        Update and log status
        """

        self.update_status_string(**kwargs)
        log(self.status)


status = PlaybackStatusDisplay()
