from time import sleep

from vlc import MediaListPlayer, MediaPlayer

from constants import DEFAULT_PB_MODE, SEEK_INTERVAL


class PlaybackController:
    def __init__(self, media_list_player: MediaListPlayer) -> None:
        self.media_list_player = media_list_player
        self.media_player: MediaPlayer = media_list_player.get_media_player()  # type: ignore

        self.playback_mode = DEFAULT_PB_MODE

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
        media = self.media_player.get_media()
        media.parse()

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

    def is_playing(self) -> bool:
        return self.media_list_player.is_playing()

    def is_paused(self) -> bool:
        return not self.is_playing() and not self.is_stopped()

    def is_stopped(self) -> None:
        return self.media_player.get_time() == -1
