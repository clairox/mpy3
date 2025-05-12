from enum import Enum

from utils import create_timestring, log


class PlaybackState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


class PlaybackStatusDisplay:
    def __init__(self, **kwargs) -> None:
        self.state = PlaybackState.STOPPED
        self.media_label = "No track selected"
        self.position = -1
        self.total_duration = -1

        self.set_attrs(**kwargs)
        self.update_status_string(**kwargs)

    def set_attrs(self, **kwargs) -> None:
        if "state" in kwargs:
            self.state = kwargs["state"]

        if "media_label" in kwargs:
            self.media_label = kwargs["media_label"]

        if "position" in kwargs:
            self.position = kwargs["position"]

        if "total_duration" in kwargs:
            self.total_duration = kwargs["total_duration"]

    def update_status_string(self, **kwargs) -> None:
        self.set_attrs(**kwargs)

        state_display = ""
        if self.state == PlaybackState.STOPPED:
            state_display = "⏹ Stopped"
        elif self.state == PlaybackState.PLAYING:
            state_display = "▶ Playing"
        elif self.state == PlaybackState.PAUSED:
            state_display = "⏸ Paused"

        status = f"{state_display:<10} |  {self.media_label}"
        if self.state != PlaybackState.STOPPED:
            status += f"  |  {create_timestring(self.position, self.total_duration)}"

        log(status)


playback_status_display = PlaybackStatusDisplay()
