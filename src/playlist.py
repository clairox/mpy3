from pathlib import Path
from typing import Union

from vlc import Media, MediaList, MediaListPlayer

import appstate
from constants import ARTIST_META, TITLE_META


class PlaylistManager:
    def __init__(self) -> None:
        self.current_idx = -1
        self.current_media: Union[Media, None] = None
        self.media_list: MediaList = MediaList()  # type: ignore

        self.media_label = "No track selected"

    def set_playlist(self, mrls: list[Path], player: MediaListPlayer) -> None:
        state = appstate.load()
        start_mrl = state.get("last_played")
        if start_mrl in mrls:
            self.current_idx = mrls.index(start_mrl)

        self.media_list: MediaList = MediaList(mrls)  # type: ignore
        player.set_media_list(self.media_list)

        self.set_current_media(self.current_idx)

    def set_current_media(self, idx: int) -> None:
        media = self.media_list.item_at_index(idx)
        media.parse()

        self.current_media = media
        self.current_idx = idx

        title = media.get_meta(TITLE_META)
        artist = media.get_meta(ARTIST_META) or "Unknown"
        self.media_label = f"{title} - {artist}"

    # def toggle_shuffle(self, value: bool) -> None:
    #     pass
