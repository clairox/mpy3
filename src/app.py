"""
Handles running the mp3 player application and processes physical
device input to control playback
"""

import sys
from enum import Enum
from pathlib import Path

from player import Player
from terminalio import getch
from utils import send_exit

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

    def __init__(self, media_dir: Path, mode: str, shuffle: bool) -> None:
        self.media_dir = media_dir
        self.player: Player = Player(mode=mode)  # type: ignore

    def run(self) -> None:
        """
        Runs the main application
        """

        media_list = [
            f
            for f in sorted(Path(self.media_dir).iterdir())
            if f.is_file() and f.suffix in ALLOWED_FILE_TYPES
        ]
        if len(media_list) == 0:
            send_exit("No media found. Exiting.")

        self.player.set_playlist(media_list)

        while True:
            key = getch()
            sys.stdout.write("\r")
            sys.stdout.flush()
            self.__handle_input(key)

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
            send_exit("Quitting.")

    def __handle_input(self, key: str) -> None:
        if key == " ":
            self.update(Control.PLAY)
        elif key in ("\x7f", "\x08"):
            self.update(Control.STOP)
        elif key == "\x1b[C":
            self.update(Control.FFORWARD)
        elif key == "\x1b[D":
            self.update(Control.REWIND)
        elif key == "n":
            self.update(Control.NEXT)
        elif key == "p":
            self.update(Control.BACK)
        elif key == "q":
            self.update(Control.QUIT)
