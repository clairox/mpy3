"""
Handles running the mp3 player application and processes physical
device input to control playback
"""

import os
import sys
from enum import Enum
from pathlib import Path

from evdev import InputDevice, InputEvent, ecodes

from player import Player

SEEK_INTERVAL = 5000
ALLOWED_FILE_TYPES = [".mp3"]


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


class App:
    """
    Main application which manages media playback and handles input controls
    """

    def __init__(self, media_dir: Path, input_device_path: Path) -> None:
        self.media_dir = media_dir
        self.input_device_path = input_device_path
        self.player: Player = Player()  # type: ignore

    def run(self) -> None:
        """
        Runs the main application
        """

        os.chdir(self.media_dir)

        media_list = [
            f
            for f in sorted(Path.cwd().iterdir())
            if f.is_file() and f.suffix in ALLOWED_FILE_TYPES
        ]
        if len(media_list) == 0:
            sys.exit("No media found. Exiting.")

        self.player.set_media_list(media_list)
        self.player.play_until_done()

        device = InputDevice(self.input_device_path)

        while True:
            for event in device.read_loop():
                self.__handle_input(event)

    def update(self, control: Control) -> None:
        """
        Updates application state on control execution

        Args:
            control (Control): Executed input control
        """

        if control == Control.PLAY:
            if self.player.is_playing():
                self.player.pause()
            else:
                self.player.play_until_done()

        elif control == Control.STOP:
            self.player.stop()

        elif control == Control.FFORWARD:
            self.player.fast_forward()

        elif control == Control.REWIND:
            self.player.rewind()

        elif control == Control.NEXT:
            self.player.next()

        elif control == Control.BACK:
            self.player.back()

        elif control == Control.QUIT:
            sys.exit("Exiting.")

    def __handle_input(self, event: InputEvent) -> None:
        if event.type != ecodes.EV_KEY:
            return

        if event.value == 1:
            if event.code == ecodes.KEY_SPACE:
                self.update(Control.PLAY)
            elif event.code == ecodes.KEY_ENTER:
                self.update(Control.STOP)
            elif event.code == ecodes.KEY_RIGHT:
                self.update(Control.FFORWARD)
            elif event.code == ecodes.KEY_LEFT:
                self.update(Control.REWIND)
            elif event.code == ecodes.KEY_N:
                self.update(Control.NEXT)
            elif event.code == ecodes.KEY_P:
                self.update(Control.BACK)
            elif event.code == ecodes.KEY_Q:
                self.update(Control.QUIT)
