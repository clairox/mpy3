"""
This is the entry point for the application. It sets up the necessary directories and 
starts the media player application by creating an instance of the `App` class and 
calling its `run()` method.
"""

from pathlib import Path

from platformdirs import user_music_dir

from app import App

MPY3_DIR = "mpy3"
INPUT_DEVICE_PATH = Path("/dev/input/event3")


if __name__ == "__main__":
    media_dir = Path(user_music_dir()) / MPY3_DIR
    media_dir.mkdir(parents=True, exist_ok=True)

    app = App(media_dir, INPUT_DEVICE_PATH)
    app.run()
