"""
This module contains the `MediaPlaybackController` class which handles
playback of a single media file
"""

# TODO Prevent fast forward/rewind from seeping into next media
# TODO Seek while paused without playing

from threading import Event as ThreadEvent
from threading import Thread
from time import sleep

from vlc import Event as VLCEvent
from vlc import Media, MediaPlayer

from enums import VLCEventType
from output import status

STOP_EVENT = ThreadEvent()
TIME_SKIP = 5000


class MediaPlaybackController:
    """
    Handles vlc.MediaPlayer playback.
    """

    def __init__(self, media: Media | None = None) -> None:
        self._media_player: MediaPlayer = MediaPlayer()  # type: ignore
        self._media: Media | None = media
        if self._media:
            self._media.parse()
            self._media_player.set_media(self._media)

        self._playback_thread = Thread(target=self.play)

        self._media_player.event_manager().event_attach(
            VLCEventType.MEDIA_PLAYER_TIME_CHANGED, self._on_time_changed
        )

    def play_until_done(self) -> None:
        """
        Starts media playback thread
        """

        self._open_playback_thread()

    def play(self) -> None:
        """
        Start media player playback.
        """

        self._media_player.play()

    def pause(self) -> None:
        """
        Pause media player playback.
        """

        self._media_player.pause()

    def stop(self) -> None:
        """
        Stop media player playback.
        """

        self._media_player.stop()

    def forward(self) -> None:
        """
        Fast forward media player playback.
        """

        time = self._media_player.get_time() + TIME_SKIP
        self._seek(time)

    def rewind(self) -> None:
        """
        Rewind media player playback.
        """

        time = self._media_player.get_time() - TIME_SKIP
        self._seek(time)

    def go_to_end(self) -> None:
        """
        DEV: Jump to last second of media playback
        """

        if self.is_stopped():
            return

        media = self._media_player.get_media()
        media.parse()
        self._media_player.set_time(media.get_duration() - 100)

    def is_playing(self) -> bool:
        """
        Returns true if media is playing, false otherwise.
        """

        return bool(self._media_player.is_playing())

    def is_stopped(self) -> bool:
        """
        Returns true if media playback is stopped, false otherwise.
        """

        return self._media_player.get_time() == -1

    def set_media(self, media: Media) -> None:
        """
        Set the media object to play.

        Args:
            media (Media): The media object
        """

        if not media.is_parsed():
            media.parse()

        self._media = media
        self._media_player.set_media(media)

    def get_time(self) -> int:
        """
        Get current time in media
        """

        return self._media_player.get_time()

    def set_time(self, time: int) -> None:
        """
        Set current media playback time

        Args:
            time (int): time in milliseconds
        """

        self._media_player.set_time(time)

    def _seek(self, time: int) -> None:
        """
        Jump to specified time in media player playback.

        Args:
            time (int): The time in milliseconds to jump to
        """

        if self._media is None:
            return

        duration = self._media.get_duration()
        if time >= duration:
            self._media_player.set_time(duration - 10)
            return

        if time <= 0:
            self._media_player.set_time(0)
            return

        is_paused = not self.is_playing and not self.is_stopped()
        if is_paused:
            self.play()
            sleep(0.01)

            self._media_player.set_time(time)
            self.pause()
        else:
            self._media_player.set_time(time)

    def _open_playback_thread(self) -> None:
        self._playback_thread = Thread(target=self.play, daemon=True)
        self._playback_thread.start()

    def close_playback_thread(self) -> None:
        """
        Close the playback thread
        """

        STOP_EVENT.set()
        self._playback_thread.join()

    def _on_time_changed(self, _: VLCEvent) -> None:
        status.update(position=self._media_player.get_time())
