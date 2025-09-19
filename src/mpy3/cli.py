import sys
from pathlib import Path

import click

from mpy3.input import Key, KeyboardListener
from mpy3.player import Media, MediaPlayer

ACCEPTED_FILE_TYPES = [".mp3"]


@click.command()
@click.argument("media_url")  # TODO: Make this optional
def main(media_url: str):
    media_url_path = Path(media_url)

    if not media_url_path.exists():
        print(f'"{media_url_path}" is not a valid file.')
        sys.exit(1)

    if media_url_path.is_file() and media_url_path.suffix not in ACCEPTED_FILE_TYPES:
        print(f'"{media_url_path}" is not a valid file type.')
        sys.exit(1)

    # TODO: Open folder as media list
    if media_url_path.is_dir():
        return

    media = Media(media_url_path)
    player = MediaPlayer(media)
    player.play_until_done()

    def handle_input(key: Key) -> None:
        if key == Key.Q:
            player.stop()

        elif key == Key.SPACE:
            if player.paused:
                player.play_until_done()
            else:
                player.pause()
        elif key == Key.LEFT:
            player.fast_forward()
        elif key == Key.RIGHT:
            player.rewind()

        # Test key
        elif key == Key.T:
            pass

    KeyboardListener().listen(handle_input)
