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


class Control(Enum):
    """
    Enum representing application commands
    """

    NONE = 0
    PLAY = 1
    FFORWARD = 2
    REWIND = 3
    QUIT = 4


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

        media_list = os.listdir(self.media_dir)
        if len(media_list) == 0:
            sys.exit("No media found. Exiting")
        else:
            self.player.set_mrl(self.media_dir / media_list[0])
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

        if control == Control.FFORWARD:
            self.player.fast_forward()

        if control == Control.REWIND:
            self.player.rewind()

        if control == Control.QUIT:
            sys.exit("Exiting.")
    def __handle_input(self, event: InputEvent) -> None:
        if event.type != ecodes.EV_KEY:
            return

        if event.value == 1:
            if event.code == ecodes.KEY_SPACE:
                self.update(Control.PLAY)
            if event.code == ecodes.KEY_RIGHT:
                self.update(Control.FFORWARD)
            if event.code == ecodes.KEY_LEFT:
                self.update(Control.REWIND)
            if event.code == ecodes.KEY_Q:
                self.update(Control.QUIT)
