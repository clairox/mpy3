"""
This module contains the `Player` class which is the entry point for
the media player, and the `MediaListPlayer` which manages the playback of
the media list
"""

import queue
import random
from pathlib import Path
from threading import Event as ThreadEvent
from threading import Thread

from vlc import Event as VLCEvent

import appstate
from enums import MediaMeta, MediaState, PlaybackMode, VLCEventType
from medialist import MediaList
from output import PlaybackState, status
from playback import MediaPlaybackController
from utils import extract_path, send_exit

STOP_EVENT = ThreadEvent()
main_thread_queue = queue.Queue()


class Player:
    """
    Handles MediaListPlayer playback.
    """

    def __init__(self, mrls: list[Path]) -> None:
        self._media_list = MediaList(mrls)
        self.media_list_player = MediaListPlayer(self._media_list)

    def play(self) -> None:
        """
        Start/resume media playback
        """

        self.media_list_player.play()

    def pause(self) -> None:
        """
        Pause media playback
        """

        self.media_list_player.pause()

    def forward(self) -> None:
        """
        Fast forward media playback
        """

        self.media_list_player.forward()

    def rewind(self) -> None:
        """
        Rewind media playback
        """

        self.media_list_player.rewind()

    def next(self) -> None:
        """
        Switch to next media in media list
        """

        self.media_list_player.next()

    def previous(self) -> None:
        """
        Switch to previous media in media list
        """

        self.media_list_player.previous()


class MediaListPlayer:
    """
    Handles playback of media from MediaList.
    """

    def __init__(self, media_list: MediaList) -> None:
        self._base_media_list = media_list
        self._media_list = self._base_media_list

        self._current_index = 0
        start_index = self._current_index
        state = appstate.load()
        start_mrl = str(state.get("last_played"))
        mrls: list[str] = [
            str(extract_path(m.get_mrl())) for m in self._base_media_list
        ]
        if start_mrl in mrls:
            start_index = mrls.index(start_mrl)

        self.pc = MediaPlaybackController()
        self._set_current_media(start_index)

        self._playback_mode = PlaybackMode.DEFAULT
        self._shuffle = False

        media_picker_thread = Thread(target=self._wait_to_select_next, daemon=True)
        media_picker_thread.start()

    def play(self) -> None:
        """
        Start media playback
        """

        self.pc.play_until_done()
        status.update(
            state=PlaybackState.PLAYING,
            position=self.pc.get_time(),
            total_duration=self._current_media.get_duration(),
        )

    def pause(self) -> None:
        """
        Pause media playback
        """

        self.pc.pause()
        status.update(state=PlaybackState.PAUSED)

    def forward(self) -> None:
        """
        Fast forward media playback
        """

        self.pc.forward()

    def rewind(self) -> None:
        """
        Rewind media playback
        """

        self.pc.rewind()

    def next(self) -> None:
        """
        Switch to next media in media list
        """

        media_list_length = len(self._media_list)

        next_idx = self._current_index + 1

        if self._playback_mode == PlaybackMode.LOOP and next_idx >= media_list_length:
            next_idx = 0

        if next_idx >= media_list_length:
            self.reset()
            if not self.pc.is_stopped():
                self.pc.close_playback_thread()
            send_exit("Playback ended")
            return

        self.change_media(next_idx)

    def previous(self) -> None:
        """
        Switch to previous media in media list
        """

        prev_idx = self._current_index - 1

        is_track_start = self.pc.get_time() <= 3000
        if self.pc.is_playing() and not is_track_start:
            self.pc.set_time(0)
            return

        if self._playback_mode == PlaybackMode.LOOP and prev_idx < 0:
            prev_idx = len(self._media_list) - 1

        if prev_idx < 0:
            self.change_media(0)
            return

        self.change_media(prev_idx)

    def change_media(self, index: int) -> None:
        """
        Switch media to media at given index in the media list.

        Args:
            index (int): Index of media in media list to change to
        """

        if self.pc.is_stopped():
            self._set_current_media(index)
            media = self._current_media
            self.pc.set_media(media)

            app_settings: appstate.AppState = {"last_played": media.get_mrl()}
            appstate.save(app_settings)

            status.update(
                media_label=self._get_media_label(),
                position=0,
                total_duration=media.get_duration(),
            )
        else:
            self._set_current_media(index)
            self.play()

    def reset(self) -> None:
        """
        Reset to beginning of media list
        """

        self.pc.stop()
        self._current_media.event_manager().event_detach(
            VLCEventType.MEDIA_STATE_CHANGED
        )

        first_media = self._media_list[0]
        app_settings: appstate.AppState = {"last_played": first_media.get_mrl()}
        appstate.save(app_settings)

    def toggle_playback_mode(self) -> None:
        """
        Toggle between default, loop, and repeat playback modes
        """

        if self._playback_mode == PlaybackMode.DEFAULT:
            self._playback_mode = PlaybackMode.LOOP

        elif self._playback_mode == PlaybackMode.LOOP:
            self._playback_mode = PlaybackMode.REPEAT

        elif self._playback_mode == PlaybackMode.REPEAT:
            self._playback_mode = PlaybackMode.DEFAULT

        status.update(playback_mode=self._playback_mode)

    def toggle_shuffle(self) -> None:
        """
        Toggle shuffle on or off
        """
        if self._shuffle:
            self._media_list = self._base_media_list
            self._current_index = self._base_media_list.index(self._current_media)

            self._shuffle = False
        else:
            population = [
                m
                for m in self._base_media_list
                if self._base_media_list.index(m) != self._current_index
            ]
            shuffled_media_list = random.sample(population, len(population))
            shuffled_media_list.insert(0, self._current_media)
            self._media_list = shuffled_media_list
            self._current_index = 0

            self._shuffle = True

        status.update(shuffle=self._shuffle)

    def is_playing(self) -> bool:
        """
        Returns true if media is playing, false otherwise.
        """

        return self.pc.is_playing()

    def _wait_to_select_next(self) -> None:
        while True:
            try:
                task = main_thread_queue.get_nowait()
                task()
            except queue.Empty:
                pass

    def _select_next(self) -> None:
        next_idx = self._current_index

        if self._playback_mode == PlaybackMode.DEFAULT:
            next_idx += 1
        elif self._playback_mode == PlaybackMode.LOOP:
            next_idx += 1
            if next_idx >= len(self._media_list):
                next_idx = 0

        if next_idx >= len(self._media_list):
            self.reset()
            self.pc.close_playback_thread()
            send_exit("Playback ended.")
            return

        app_settings: appstate.AppState = {"last_played": self._current_media.get_mrl()}
        appstate.save(app_settings)

        self._set_current_media(next_idx)
        self.pc.set_media(self._current_media)
        self.play()

    def _set_current_media(self, index: int) -> None:
        media = self._media_list[index]
        media.parse()
        self._current_media = media
        self._current_media.event_manager().event_attach(
            VLCEventType.MEDIA_STATE_CHANGED, self._on_media_state_changed
        )
        self.pc.set_media(self._current_media)
        self._current_index = index

        status.update(media_label=self._get_media_label())

    def _on_media_state_changed(self, _: VLCEvent) -> None:
        state = self._current_media.get_state()

        if state == MediaState.ENDED:
            self._current_media.event_manager().event_detach(
                VLCEventType.MEDIA_STATE_CHANGED
            )

            self.pc.close_playback_thread()
            main_thread_queue.put(self._select_next)

    def _get_media_label(self) -> str:
        title = self._current_media.get_meta(MediaMeta.TITLE)
        artist = self._current_media.get_meta(MediaMeta.ARTIST) or "Unknown"
        return f"{title} - {artist}"
