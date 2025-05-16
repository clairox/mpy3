"""
This module contains the `MediaList` class which represents a 
list of media files
"""

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

    def index(self, media: Media) -> int:
        """
        Looks up the index of a media file, returns -1 if media is not in list.

        Args:
            media (Media): Media file to lookup

        Returns:
            int: index of media file, -1 if media not in list
        """

        for i, _ in enumerate(self._media_list):
            if self._media_list[i] == media:
                return i
        return -1

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
