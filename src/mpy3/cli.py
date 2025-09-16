import sys
from pathlib import Path

import click

from mpy3.player import Media, MediaPlayer

ACCEPTED_FILE_TYPES = [".mp3"]


@click.command()
@click.argument("media_url")  # TODO: Make this optional
def main(media_url: str):
    media_url_path = Path(media_url)

    if not media_url_path.exists():
        print(f'"{media_url_path}" is not a valid file.')
        sys.exit(1)

    if media_url_path.suffix not in ACCEPTED_FILE_TYPES:
        print(f'"{media_url_path}" is not a valid file type.')
        sys.exit(1)

    media = Media(media_url_path)
    player = MediaPlayer(media)
    player.play_until_done()

    pass
