"""
Handles running the mp3 player application and processes physical
device input to control playback
"""

import sys
from enum import Enum
from pathlib import Path
from threading import Thread, current_thread
from time import sleep

# from events import PlayerEventHandler
from player import Player
from q import main_thread_queue, queue
from terminalio import getch
from utils import log, send_exit

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
    TOGGLE_MODE = 8
    TOGGLE_SHUFFLE = 9


# class KeypressListener:
#     def __init__(self) -> None:
#         self._thread = Thread(target=self._listen)
#
#     def start(self) -> None:
#         keypress_listener = Thread(target=self.a)
#         keypress_listener.daemon = True
#         keypress_listener.start()
#
#     def _listen(self) -> None:
#         while True:
#             key = getch()
#             sys.stdout.write("\r")
#             sys.stdout.flush()
#             self._handle_input(key)
#
#     def _handle_input(self, key: str) -> None:


class App:
    """
    Main application which manages media playback and handles input controls
    """

    def __init__(self, media_dir: Path) -> None:
        mrls = self._load_mrls(media_dir)
        if len(mrls) == 0:
            send_exit("No media found. Exiting.")

        self.player = Player(mrls)
        # self.event_handler = PlayerEventHandler(self.player)

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

        ml_player = self.player.media_list_player
        # pm = self.player.pm
        #
        if control == Control.PLAY:
            if ml_player.is_playing():
                ml_player.pause()
            else:
                ml_player.play()
        #
        # elif control == Control.STOP:
        #     pc.stop()
        #
        # elif control == Control.FFORWARD:
        #     pc.fast_forward()
        #
        # elif control == Control.REWIND:
        #     pc.rewind()
        #
        elif control == Control.NEXT:
            ml_player.next()

        elif control == Control.BACK:
            ml_player.previous()

        elif control == Control.QUIT:
            ml_player.pc.stop()
            send_exit("Quitting.")

        elif control == Control.TOGGLE_MODE:
            ml_player.toggle_playback_mode()

        elif control == Control.TOGGLE_SHUFFLE:
            ml_player.toggle_shuffle()

    def _handle_input(self, key: str) -> None:
        ml_player = self.player.media_list_player
        if key == " ":
            self.update(Control.PLAY)
        # elif key in ("\x7f", "\x08"):
        #     self.update(Control.STOP)
        # elif key == "\x1b[C":
        #     self.update(Control.FFORWARD)
        # elif key == "\x1b[D":
        #     self.update(Control.REWIND)
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
