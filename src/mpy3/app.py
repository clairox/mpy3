from pathlib import Path

from mpy3.player import Media

DEFAULT_MEDIA_DIR = Path.home() / "mpy3/tracks/"


class App:
    def __init__(self) -> None:
        media_dir = Path(DEFAULT_MEDIA_DIR)
        if not media_dir.exists():
            Path.mkdir(media_dir, parents=True)

        unsorted_media_list: list[Media] = []
        for mrl in media_dir.iterdir():
            media = Media(mrl)
            media.parse_meta()
            unsorted_media_list.append(media)

        media_list = sorted(unsorted_media_list, key=lambda media: media.title)
