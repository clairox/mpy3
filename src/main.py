"""
This is the entry point for the application. It sets up the necessary directories and 
starts the media player application by creating an instance of the `App` class and 
calling its `run()` method.
"""

import argparse
import sys
from pathlib import Path

from platformdirs import user_music_dir

from app import App
from utils import send_exit

MPY3_DIR = "mpy3"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="mpy3", description="Just a simple mp3 player"
    )
    parser.add_argument(
        "-d", "--dir", type=Path, help="Path to directory containing media files"
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["default", "loop", "repeat"],
        default="default",
        help="Playback mode: default, loop playlist, repeat current track",
    )
    parser.add_argument(
        "-s", "--shuffle", action="store_true", help="Shuffle playback order"
    )

    args = parser.parse_args()

    media_dir = Path()
    if args.dir is None:
        media_dir = Path(user_music_dir()) / MPY3_DIR
    else:
        media_dir = Path(args.dir)
    media_dir.mkdir(parents=True, exist_ok=True)

    playback_mode = args.mode
    shuffle = args.shuffle

    app = App(media_dir, playback_mode, shuffle)
    app.run()
