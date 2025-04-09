"""
app.py

This module defines the `App` class, which provides functionality for playing, pausing, 
stopping, and seeking through an audio file. It also listens for keyboard inputs to control 
the media player and allows interaction with the media player through specific key events.

"""

import os
import threading
from pathlib import Path
from time import sleep

from evdev import InputDevice, InputEvent, ecodes
from vlc import MediaPlayer

from duration import Duration
from utils import time_from_ms

KEYBOARD_PATH = "/dev/input/event3"
SEEK_INTERVAL = 5000


class App:
    """
    A class to control and manage the playback of an audio file using VLC media player.

    Args:
        media_dir (Path): The directory where the media file is located.

    """

    def __init__(self, media_dir: Path) -> None:
        self.media_dir = media_dir
        self.player: MediaPlayer = MediaPlayer()  # type: ignore
        self.current_media_file = ""
        self.current_time = Duration(0)

    def run(self) -> None:
        """
        Starts the playback of the media file and begins listening for user input.
        """
        media_list = os.listdir(self.media_dir)
        if len(media_list) == 0:
            print("No media found. Exiting")
        else:
            self.player.set_mrl(self.media_dir / media_list[0])
            self.current_media_file = media_list[0]
            self.play()

    def play(self) -> None:
        """
        Plays the media file and starts a background thread to listen for keypress events.
        """

        try:
            self.player.play()

            sleep(0.1)

            track_length = Duration(self.player.get_length())
            print(f"Playing {self.current_media_file}")

            keypress_thread = threading.Thread(target=self.listen)
            keypress_thread.daemon = True
            keypress_thread.start()

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

    def pause(self) -> None:
        """
        Pauses the media playback and prints the current playback time.
        """

        try:
            self.player.pause()
            print(f"Paused at {time_from_ms(self.current_time.to_millis())}")
        except Exception as e:
            print(f"Could not pause media: {e}")

    def stop(self) -> None:
        """
        Stops the media playback.
        """

        try:
            self.player.stop()
        except Exception as e:
            print(f"Could not stop media: {e}")

    def fast_forward(self) -> None:
        """
        Fast-forwards the media playback by the predefined seek interval.
        """

        try:
            self.seek(self.current_time.to_millis() + SEEK_INTERVAL)
        except Exception as e:
            print(f"Could not fast forward: {e}")

    def rewind(self) -> None:
        """
        Rewinds the media playback by the predefined seek interval.
        """

        try:
            self.seek(self.current_time.to_millis() - SEEK_INTERVAL)
        except Exception as e:
            print(f"Could not rewind: {e}")

    def seek(self, time) -> None:
        """
        Seeks to the specified time in the media file.

        If the specified time is beyond the track length, the media is stopped. If the time is less than or equal
        to 0, the media starts from the beginning. Otherwise, the media is paused after seeking to the specified time.

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

    def listen(self) -> None:
        """
        Listens for keyboard events and triggers corresponding actions (play/pause, fast-forward, rewind).
        """

        device = InputDevice(KEYBOARD_PATH)

        for event in device.read_loop():
            if self.categorize(event) == "SPACE":
                if self.player.is_playing():
                    self.pause()
                else:
                    self.play()
            if self.categorize(event) == "RIGHT":
                self.fast_forward()
            if self.categorize(event) == "LEFT":
                self.rewind()

    def categorize(self, event: InputEvent) -> str:
        """
        Categorizes the key event based on the key pressed.

        Args:
            event (InputEvent): The input event to categorize.

        Returns:
            str: The corresponding action as a string ("SPACE", "RIGHT", "LEFT").
        """

        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                if event.code == ecodes.KEY_SPACE:
                    return "SPACE"
                if event.code == ecodes.KEY_RIGHT:
                    return "RIGHT"
                if event.code == ecodes.KEY_LEFT:
                    return "LEFT"

        return ""
