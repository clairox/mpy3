from pathlib import Path

from mpy3.gui.core import App

DEFAULT_MEDIA_DIR = Path.home() / "mpy3/tracks/"


def main():
    media_dir = Path(DEFAULT_MEDIA_DIR)
    if not media_dir.exists():
        Path.mkdir(media_dir, parents=True)

    app = App(media_dir)
    app.run()


if __name__ == "__main__":
    main()
