"""
This module contains the `Player` class which handles media playback
using vlc.MediaPlayer
"""

from pathlib import Path
from threading import Event as ThreadEvent
from threading import Thread
from time import sleep

from vlc import (
    Event,
    EventType,
    Media,
    MediaListPlayer,
    MediaPlayer,
    Meta,
    PlaybackMode,
    State,
)

import appstate
from appstate import AppState
from output import PlaybackState, PlaybackStatusDisplay
from playlist import PlaylistManager
from utils import send_exit

SEEK_INTERVAL = 5000
STOP_EVENT = ThreadEvent()

# vlc.EventTypes
MEDIA_STATE_CHANGED_EVENT_TYPE = EventType(5)
MEDIA_PLAYER_MEDIA_CHANGED_EVENT_TYPE = EventType(0x100)
MEDIA_PLAYER_TIME_CHANGED = EventType(267)

# vlc.States
IDLE_STATE = State(0)
PLAYING_STATE = State(3)
PAUSED_STATE = State(4)
STOPPING_STATE = State(5)
ENDED_STATE = State(6)

# vlc.PlaybackModes
DEFAULT_PB_MODE = PlaybackMode(0)
LOOP_PB_MODE = PlaybackMode(1)
REPEAT_PB_MODE = PlaybackMode(2)

# vlc.Metas
TITLE_META = Meta(0)
ARTIST_META = Meta(1)


class Player:
    """
    Handles vlc.MediaListPlayer playback
    """

    def __init__(self, mode: str):
        self.player: MediaListPlayer = MediaListPlayer()  # type: ignore
        self.pm = PlaylistManager()

        if mode == "loop":
            self.playback_mode = LOOP_PB_MODE
        elif mode == "repeat":
            self.playback_mode = REPEAT_PB_MODE
        else:
            self.playback_mode = DEFAULT_PB_MODE

        self.player.set_playback_mode(self.playback_mode)

        self.current_media_player: MediaPlayer = self.player.get_media_player()

        self.playback_thread: Thread = Thread(target=self.play)

        self.media_starting = False

        self.status_display = PlaybackStatusDisplay(
            state=PlaybackState.STOPPED, media_label=self.pm.media_label
        )

        self.current_media_player.event_manager().event_attach(
            MEDIA_PLAYER_MEDIA_CHANGED_EVENT_TYPE, self.on_play_begin
        )

        self.current_media_player.event_manager().event_attach(
            MEDIA_PLAYER_TIME_CHANGED, self.on_time_changed
        )

    # Playback

    def play_until_done(self) -> None:
        """
        Starts media playback thread
        """

        self.playback_thread = Thread(target=self.play)
        self.playback_thread.daemon = True
        self.playback_thread.start()

    def play(self) -> None:
        """
        Start media playback of queued media
        """

        try:
            if self.is_stopped():
                self.player.play_item_at_index(self.pm.current_idx)
            else:
                self.player.play()

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Could not play media: {e}")

    def pause(self) -> None:
        """
        Pauses media playback if media is playing
        """

        try:
            self.player.pause()

        except Exception as e:
            print(f"Could not pause media: {e}")

    def stop(self) -> None:
        """
        Stop media playback and clear the queue
        """

        try:
            self.current_media_player.stop()
        except Exception as e:
            print(f"Could not stop media: {e}")

    def fast_forward(self) -> None:
        """
        Fast forwards media playback by predefined seek interval
        """

        try:
            time = self.current_media_player.get_time() + SEEK_INTERVAL
            self.seek(time)
        except Exception as e:
            print(f"Could not fast forward: {e}")

    def rewind(self) -> None:
        """
        Rewinds media playback by predefined seek interval
        """

        try:
            time = self.current_media_player.get_time() - SEEK_INTERVAL
            self.seek(time)
        except Exception as e:
            print(f"Could not rewind: {e}")

    def next(self) -> None:
        """
        Skips to next item in media list
        """

        media_list_count = self.pm.media_list.count()
        current_idx = self.pm.current_idx

        try:
            if self.is_stopped() and current_idx < media_list_count - 1:
                self.pm.set_current_media(current_idx + 1)
                self.status_display.update_status_string(
                    media_label=self.pm.media_label
                )
                return

            next_idx = current_idx + 1
            if next_idx >= media_list_count:
                if self.playback_mode in (DEFAULT_PB_MODE, REPEAT_PB_MODE):
                    self.stop()
                    return

            if self.playback_mode == REPEAT_PB_MODE:
                self.player.play_item_at_index(next_idx)
                return

            self.pm.set_current_media(current_idx + 1)
            self.player.play_item_at_index(self.pm.current_idx)
        except Exception as e:
            print(f"Could not play next track: {e}")

    def back(self) -> None:
        """
        Skips to previous item in media list or go back to media start

        Sets time to 0 if past 3 seconds into media
        """

        current_idx = self.pm.current_idx

        try:
            if self.is_stopped() and current_idx > 0:
                self.pm.set_current_media(current_idx - 1)
                self.status_display.update_status_string(
                    media_label=self.pm.media_label
                )
                return

            is_track_start = self.current_media_player.get_time() <= 3000
            if not is_track_start:
                self.current_media_player.set_time(0)
                return

            previous_index = current_idx - 1
            if previous_index < 0:
                if self.playback_mode in (DEFAULT_PB_MODE, REPEAT_PB_MODE):
                    self.player.play_item_at_index(0)
                    return

            if self.playback_mode == REPEAT_PB_MODE:
                self.player.play_item_at_index(previous_index)
                return

            self.pm.set_current_media(current_idx - 1)
            self.player.play_item_at_index(self.pm.current_idx)
        except Exception as e:
            print(f"Could not play next track: {e}")

    def seek(self, t: int) -> None:
        """
        Seeks to the specified time in the media file.

        If the specified time is beyond the track length, the
        media is stopped. If the time is less than or equal to
        0, the media starts from the beginning. Otherwise, the
        media is paused after seeking to the specified time.

        Args:
            t (int): The time to seek to, in milliseconds.
        """

        if self.pm.current_media is None:
            return

        duration = self.pm.current_media.get_duration()
        if t > duration:
            self.current_media_player.set_time(duration)
        elif t <= 0:
            self.current_media_player.set_time(0)
        else:
            if not self.player.is_playing():
                self.player.play()
                sleep(0.01)
                self.current_media_player.set_time(t)
                self.player.pause()
            else:
                self.current_media_player.set_time(t)

    # Callbacks

    def on_media_state_change(self, _: Event) -> None:
        """
        Event callback executed on media state changes
        """

        if self.pm.current_media is None:
            return

        state = self.pm.current_media.get_state()

        def reset() -> None:
            if self.pm.current_media is None:
                return

            self.pm.current_media.event_manager().event_detach(EventType(5))
            self.current_media_player = self.player.get_media_player()

            m: Media = self.pm.media_list.item_at_index(0)  # type: ignore
            app_settings: AppState = {"last_played": m.get_mrl()}
            appstate.save(app_settings)

            STOP_EVENT.set()
            self.playback_thread.join()

        if state == IDLE_STATE:
            self.pm.current_media.event_manager().event_detach(EventType(5))
        elif state == PLAYING_STATE:
            if self.media_starting is True:
                self.media_starting = False
            else:
                self.status_display.update_status_string(
                    state=PlaybackState.PLAYING,
                    media_label=self.pm.media_label,
                    position=self.current_media_player.get_time(),
                    total_duration=self.pm.current_media.get_duration(),
                )
        elif state == PAUSED_STATE:
            self.status_display.update_status_string(
                state=PlaybackState.PAUSED,
                position=self.current_media_player.get_time(),
            )
        elif state == STOPPING_STATE:
            reset()
            send_exit("Playback stopped.")
        elif state == ENDED_STATE:
            if self.pm.current_idx == self.pm.media_list.count() - 1:
                if self.playback_mode == DEFAULT_PB_MODE:
                    reset()
                    send_exit("Playback ended.")

    def on_play_begin(self, _: Event) -> None:
        """
        Event callback executed when next media playback begins
        """
        media = self.pm.current_media

        if media is None:
            return

        media.event_manager().event_attach(
            MEDIA_STATE_CHANGED_EVENT_TYPE, self.on_media_state_change
        )

        self.media_starting = True

        app_settings: AppState = {"last_played": media.get_mrl()}
        appstate.save(app_settings)

        self.status_display.update_status_string(
            state=PlaybackState.PLAYING,
            media_label=self.pm.media_label,
            position=0,
            total_duration=media.get_duration(),
        )

    def on_time_changed(self, _: Event) -> None:
        if self.pm.current_media is None:
            return

        if self.current_media_player.get_time():
            self.status_display.update_status_string(
                position=self.current_media_player.get_time(),
                total_duration=self.pm.current_media.get_duration(),
            )

    # Utils

    def is_playing(self) -> bool:
        """
        Returns True if media is being played, False otherwise
        """

        return bool(self.player.is_playing())

    def is_stopped(self) -> bool:
        """
        Returns True if media player is stopped, False otherwise
        """

        return self.current_media_player.get_time() == -1

    def set_playlist(self, mrls: list[Path]) -> None:
        self.pm.set_playlist(mrls, self.player)
        self.status_display.update_status_string(media_label=self.pm.media_label)

    # def set_media_list(self, mrls: list[Path]) -> None:
    #     """
    #     Queue up media file for playback
    #     """
    #
    #     state = appstate.load()
    #     start = state.get("last_played")
    #
    #     l = random.sample(mrls, len(mrls)) if self.shuffle else mrls
    #
    #     if start in l:
    #         if self.shuffle:
    #             l = [start] + [p for p in l if p != start]
    #             self.start_idx = 0
    #         else:
    #             self.start_idx = l.index(start)
    #
    #     self.media_list = MediaList(l)  # type: ignore
    #     self.player.set_media_list(self.media_list)
    #
    #     self.set_current_track(self.start_idx)
