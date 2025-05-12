from threading import Event as ThreadEvent
from threading import Thread
from time import sleep

from vlc import MediaListPlayer, MediaPlayer

from constants import SEEK_INTERVAL
from playlist import PlaylistManager

STOP_EVENT = ThreadEvent()


class PlaybackController:
    def __init__(
        self, media_list_player: MediaListPlayer, playlist_manager: PlaylistManager
    ) -> None:
        self.media_list_player = media_list_player
        self.media_player: MediaPlayer = media_list_player.get_media_player()  # type: ignore
        self.pm = playlist_manager

        self.playback_thread: Thread = Thread(target=self.play)

    def play_until_done(self) -> None:
        """
        Starts media playback thread
        """

        self.playback_thread = Thread(target=self.play)
        self.playback_thread.daemon = True
        self.playback_thread.start()

    def play(self) -> None:
        try:
            if self.is_stopped():
                self.media_list_player.play_item_at_index(self.pm.current_idx)
            else:
                self.media_list_player.play()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Could not play media: {e}")

    def pause(self) -> None:
        try:
            self.media_list_player.pause()
        except Exception as e:
            print(f"Could not pause media: {e}")

    def stop(self) -> None:
        try:
            self.media_player.stop()
        except Exception as e:
            print(f"Could not stop media: {e}")

    def next(self) -> None:
        playlist_length = self.pm.media_list.count()
        current_idx = self.pm.current_idx

        try:
            next_idx = current_idx + 1

            if self.is_stopped():
                if next_idx < playlist_length:
                    self.pm.set_current_media(next_idx)
                    return
                return

            if next_idx >= playlist_length:
                self.stop()
                return

            self.pm.set_current_media(next_idx)
            self.media_list_player.play_item_at_index(next_idx)

        except Exception as e:
            print(f"Could not play next track: {e}")

    def back(self) -> None:
        current_idx = self.pm.current_idx
        try:
            prev_idx = current_idx - 1

            if self.is_stopped():
                if prev_idx >= 0:
                    self.pm.set_current_media(prev_idx)
                    return
                return

            is_track_start = self.media_player.get_time() <= 3000
            if not is_track_start:
                self.media_player.set_time(0)
                return

            if prev_idx < 0:
                self.media_list_player.play_item_at_index(0)

            self.pm.set_current_media(prev_idx)
            self.media_list_player.play_item_at_index(prev_idx)
        except Exception as e:
            print(f"Could not play next track: {e}")

    def fast_forward(self) -> None:
        try:
            time = self.media_player.get_time() + SEEK_INTERVAL
            self.seek(time)
        except Exception as e:
            print(f"Could not fast forward: {e}")

    def rewind(self) -> None:
        try:
            time = self.media_player.get_time() - SEEK_INTERVAL
            self.seek(time)
        except Exception as e:
            print(f"Could not fast forward: {e}")

    def seek(self, position: int) -> None:
        media = self.pm.current_media
        if media is None:
            return

        duration = media.get_duration()
        if position >= duration:
            self.media_player.set_time(duration - 10)
            return

        if position <= 0:
            self.media_player.set_time(0)
            return

        if self.is_paused():
            self.media_list_player.play()

            sleep(0.1)

            self.media_player.set_time(position)
            self.media_list_player.pause()
        else:
            self.media_player.set_time(position)

    def close_thread(self) -> None:
        STOP_EVENT.set()
        self.playback_thread.join()

    def is_playing(self) -> bool:
        return self.media_list_player.is_playing()

    def is_paused(self) -> bool:
        return not self.is_playing() and not self.is_stopped()

    def is_stopped(self) -> None:
        return self.media_player.get_time() == -1
