"""
Handles running the mp3 player application and processes physical
device input to control playback
"""

import sys
from pathlib import Path

from enums import Control
from player import Player
from terminalio import getch
from utils import send_exit

ALLOWED_FILE_TYPES = [".mp3"]


class App:
    """
    Main application which manages media playback and handles input controls
    """

    def __init__(self, media_dir: Path) -> None:
        mrls = self._load_mrls(media_dir)
        if len(mrls) == 0:
            send_exit("No media found. Exiting.")

        self.player = Player(mrls)

    def run(self) -> None:
        """
        Runs the main application
        """

        while True:
            key = getch()
            sys.stdout.write("\r")
            sys.stdout.flush()
            self._handle_input(key)

    def update(self, control: Control) -> None:
        """
        Updates application state on control execution

        Args:
            control (Control): Executed input control
        """

        player = self.player.media_list_player

        if control == Control.PLAY:
            if player.is_playing():
                player.pause()
            else:
                player.play()
        #
        # elif control == Control.STOP:
        #     pc.stop()
        #
        elif control == Control.FFORWARD:
            player.forward()

        elif control == Control.REWIND:
            player.rewind()

        elif control == Control.NEXT:
            player.next()

        elif control == Control.BACK:
            player.previous()

        elif control == Control.QUIT:
            player.pc.stop()
            send_exit("Quitting.")

        elif control == Control.TOGGLE_MODE:
            player.toggle_playback_mode()

        elif control == Control.TOGGLE_SHUFFLE:
            player.toggle_shuffle()

    def _handle_input(self, key: str) -> None:
        ml_player = self.player.media_list_player
        if key == " ":
            self.update(Control.PLAY)
        # elif key in ("\x7f", "\x08"):
        #     self.update(Control.STOP)
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
        elif key == "m":
            self.update(Control.TOGGLE_MODE)
        elif key == "s":
            self.update(Control.TOGGLE_SHUFFLE)
        elif key == "i":
            ml_player.pc.go_to_end()

    def _load_mrls(self, media_dir: Path) -> list[Path]:
        """
        Retrieve valid mrls from a given directory.

        Args:
            media_dir (Path): The directory to load mrls from.

        Returns:
            list[Path]: A list of valid mrls
        """

        paths = sorted(Path(media_dir).iterdir())

        def is_valid_file(p: Path) -> bool:
            return p.is_file() and p.suffix in ALLOWED_FILE_TYPES

        return [p for p in paths if is_valid_file(p)]
