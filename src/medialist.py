from pathlib import Path

from vlc import Media


class MediaList:
    """
    List of playable media.
    """

    def __init__(self, mrls: list[Path]) -> None:
        self._media_list: list[Media] = []
        for mrl in mrls:
            media: Media = Media(mrl)  # type: ignore
            self._media_list.append(media)

    def __repr__(self) -> str:
        r = "{ "
        count = len(self._media_list)
        for i in range(0, count):
            filename = Path(self._media_list[i].get_mrl()).name
            if i < count - 1:
                r += f'{i}: "{filename}", '
            else:
                r += f'{i}: "{filename}" }}'

        return r

    def __len__(self) -> int:
        return len(self._media_list)

    def __getitem__(self, index: int) -> Media:
        return self._media_list[index]

    def index(self, media: Media) -> int:
        for i, _ in enumerate(self._media_list):
            if self._media_list[i] == media:
                return i
        return -1
