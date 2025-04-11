"""
This module contains the `Player` class which handles media playback
using vlc.MediaPlayer
"""

import random
from pathlib import Path
from threading import Event as ThreadEvent
from threading import Thread
from time import sleep

from vlc import (
    Event,
    EventType,
    Media,
    MediaList,
    MediaListPlayer,
    MediaPlayer,
    PlaybackMode,
    State,
)

from utils import log, send_exit, time_from_ms

SEEK_INTERVAL = 5000
STOP_EVENT = ThreadEvent()

# vlc.EventTypes
MEDIA_STATE_CHANGED_EVENT_TYPE = EventType(5)
MEDIA_PLAYER_MEDIA_CHANGED_EVENT_TYPE = EventType(0x100)

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


class Player:
    """
    Handles vlc.MediaListPlayer playback
    """

    def __init__(self, mode: str, shuffle: bool):
        self.player: MediaListPlayer = MediaListPlayer()  # type: ignore
        self.media_list: MediaList = MediaList([])  # type: ignore

        if mode == "loop":
            self.playback_mode = LOOP_PB_MODE
        elif mode == "repeat":
            self.playback_mode = REPEAT_PB_MODE
        else:
            self.playback_mode = DEFAULT_PB_MODE

        self.shuffle = shuffle

        self.player.set_playback_mode(self.playback_mode)

        self.current_media_player: MediaPlayer = self.player.get_media_player()
        self.current_media: Media = self.current_media_player.get_media()

        self.playback_thread: Thread = Thread(target=self.play)

        self.media_starting = False

        self.current_media_player.event_manager().event_attach(
            MEDIA_PLAYER_MEDIA_CHANGED_EVENT_TYPE, self.on_play_begin
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
                self.player.play_item_at_index(0)
            else:
                self.player.play()

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Count not play media: {e}")

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

        try:
            if self.is_stopped():
                return

            next_idx = self.current_idx() + 1
            if next_idx >= self.media_list.count():
                if self.playback_mode in (DEFAULT_PB_MODE, REPEAT_PB_MODE):
                    self.stop()
                    return

            if self.playback_mode == REPEAT_PB_MODE:
                self.player.play_item_at_index(next_idx)
                return

            self.player.next()
        except Exception as e:
            print(f"Could not play next track: {e}")

    def back(self) -> None:
        """
        Skips to previous item in media list or go back to media start

        Sets time to 0 if past 3 seconds into media
        """

        try:
            if self.is_stopped():
                return

            is_track_start = self.current_media_player.get_time() <= 3000
            if not is_track_start:
                self.current_media_player.set_time(0)
                return

            previous_index = self.current_idx() - 1
            if previous_index < 0:
                if self.playback_mode in (DEFAULT_PB_MODE, REPEAT_PB_MODE):
                    self.player.play_item_at_index(0)
                    return

            if self.playback_mode == REPEAT_PB_MODE:
                self.player.play_item_at_index(previous_index)
                return

            self.player.previous()
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

        duration = self.current_media.get_duration()
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

        state = self.current_media.get_state()

        filename = Path(self.current_media.get_mrl()).name

        def reset() -> None:
            self.current_media.event_manager().event_detach(EventType(5))
            self.current_media_player = self.player.get_media_player()
            self.current_media = self.current_media_player.get_media()

            STOP_EVENT.set()
            self.playback_thread.join()

        if state == IDLE_STATE:
            self.current_media.event_manager().event_detach(EventType(5))
        elif state == PLAYING_STATE:
            if self.media_starting is True:
                self.media_starting = False
            else:
                log(f"{filename} - Playing")
        elif state == PAUSED_STATE:
            log(
                f"{filename} - Paused at {time_from_ms(self.current_media_player.get_time())}"
            )
        elif state == STOPPING_STATE:
            reset()
            send_exit("Playback stopped.")
        elif state == ENDED_STATE:
            if self.current_idx() == self.media_list.count() - 1:
                if self.playback_mode == DEFAULT_PB_MODE:
                    reset()
                    send_exit("Playback ended.")

    def on_play_begin(self, _: Event) -> None:
        """
        Event callback executed when next media playback begins
        """

        media: Media = self.current_media_player.get_media()  # type: ignore
        media.parse()
        self.current_media = media
        self.current_media.event_manager().event_attach(
            MEDIA_STATE_CHANGED_EVENT_TYPE, self.on_media_state_change
        )

        self.media_starting = True

        filename = Path(media.get_mrl()).name
        log(f"{filename} - Playing")

    # Utils

    def current_idx(self) -> int:
        """
        Index of currently playing media in media list
        """

        return self.media_list.index_of_item(self.current_media)

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

    def set_media_list(self, mrls: list[Path]) -> None:
        """
        Queue up media file for playback
        """

        l = []
        if self.shuffle:
            l = random.sample(mrls, len(mrls))

        self.media_list = MediaList(l)  # type: ignore
        self.player.set_media_list(self.media_list)
