"""
This module contains the `Player` class which handles media playback
using vlc.MediaPlayer
"""

from pathlib import Path
from threading import Thread
from time import sleep

from vlc import MediaPlayer

from duration import Duration
from utils import time_from_ms

SEEK_INTERVAL = 5000


class Player:
    """
    Handles vlc.MediaPlayer playback
    """

    def __init__(self):
        self.player: MediaPlayer = MediaPlayer()  # type: ignore
        self.filename = ""
        self.current_time = Duration(-1)

    def fast_forward(self) -> None:
        """
        Fast forwards media playback by predefined seek interval
        """

        try:
            self.seek(self.current_time.to_millis() + SEEK_INTERVAL)
        except Exception as e:
            print(f"Could not fast forward: {e}")

    def is_playing(self) -> bool:
        """
        Returns True if media is being played, False otherwise
        """

        return bool(self.player.is_playing())

    def pause(self) -> None:
        """
        Pauses media playback if media is playing
        """

        try:
            self.player.pause()
            print(f"Paused at {time_from_ms(self.current_time.to_millis())}")
        except Exception as e:
            print(f"Could not pause media: {e}")

    def play_until_done(self) -> None:
        """
        Starts media playback thread
        """

        thread = Thread(target=self.play)
        thread.daemon = True
        thread.start()

    def play(self) -> None:
        """
        Start media playback of queued media
        """

        try:
            print(self.filename)
            self.player.play()

            sleep(0.1)

            track_length = Duration(self.player.get_length())
            print(f"Playing {self.filename}")
            while (
                self.player.get_length() != -1
                and self.current_time.to_secs() < track_length.to_secs()
            ):
                if (
                    self.current_time.to_secs()
                    != Duration(self.player.get_time()).to_secs()
                ):
                    self.current_time = Duration(self.player.get_time())

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Count not play media: {e}")

    def rewind(self) -> None:
        """
        Rewinds media playback by predefined seek interval
        """

        try:
            self.seek(self.current_time.to_millis() - SEEK_INTERVAL)
        except Exception as e:
            print(f"Could not rewind: {e}")

    def seek(self, time) -> None:
        """
        Seeks to the specified time in the media file.

        If the specified time is beyond the track length, the
        media is stopped. If the time is less than or equal to
        0, the media starts from the beginning. Otherwise, the
        media is paused after seeking to the specified time.

        Args:
            time (int): The time to seek to, in milliseconds.
        """

        if time >= self.player.get_length():
            self.stop()
        elif time <= 0:
            self.player.set_time(0)
        else:
            if not self.player.is_playing():
                self.player.play()
                sleep(0.01)
                self.player.set_time(time)
                self.player.pause()
            else:
                self.player.set_time(time)

    def set_mrl(self, mrl: Path) -> None:
        """
        Queue up media file for playback
        """

        self.player.set_mrl(str(mrl))
        self.filename = mrl.name

    def stop(self) -> None:
        """
        Stop media playback and clear the queue
        """

        try:
            self.player.stop()
            self.filename = ""
            self.current_time = Duration(-1)
        except Exception as e:
            print(f"Could not stop media: {e}")
