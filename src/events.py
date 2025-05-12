from vlc import Event as VLCEvent

import appstate
from appstate import AppState
from constants import (
    DEFAULT_PB_MODE,
    ENDED_STATE,
    IDLE_STATE,
    MEDIA_PLAYER_MEDIA_CHANGED_EVENT_TYPE,
    MEDIA_PLAYER_TIME_CHANGED,
    MEDIA_STATE_CHANGED_EVENT_TYPE,
    PAUSED_STATE,
    PLAYING_STATE,
    STOPPING_STATE,
)
from output import PlaybackState, playback_status_display
from player import Player
from utils import send_exit


class PlayerEventHandler:
    def __init__(self, player: Player) -> None:
        self.media_player = player.current_media_player
        self.pm = player.pm
        self.pc = player.pc
        self.reset = player.reset

        self.media_player.event_manager().event_attach(
            MEDIA_PLAYER_MEDIA_CHANGED_EVENT_TYPE, self.on_play_begin
        )
        self.media_player.event_manager().event_attach(
            MEDIA_PLAYER_TIME_CHANGED, self.on_media_player_time_changed
        )

    def on_play_begin(self, _: VLCEvent) -> None:
        self.pm.set_current_media(
            self.pm.media_list.index_of_item(self.pc.media_player.get_media())
        )

        media = self.pm.current_media
        if media is None:
            return

        media.event_manager().event_attach(
            MEDIA_STATE_CHANGED_EVENT_TYPE, self.on_media_state_changed
        )

        app_settings: AppState = {"last_played": media.get_mrl()}
        appstate.save(app_settings)

        playback_status_display.update_status_string(
            state=PlaybackState.PLAYING,
            media_label=self.pm.media_label,
            position=0,
            total_duration=media.get_duration(),
        )

    def on_media_player_time_changed(self, _: VLCEvent) -> None:
        media = self.pm.current_media
        if media is None:
            return

        if self.media_player.get_time():
            playback_status_display.update_status_string(
                position=self.media_player.get_time(),
                total_duration=media.get_duration(),
            )

    def on_media_state_changed(self, _: VLCEvent) -> None:
        media = self.pm.current_media
        if media is None:
            return

        state = media.get_state()

        if state == IDLE_STATE:
            media.event_manager().event_detach(MEDIA_STATE_CHANGED_EVENT_TYPE)

        elif state == PLAYING_STATE:
            playback_status_display.update_status_string(
                state=PlaybackState.PLAYING,
                media_label=self.pm.media_label,
                position=self.media_player.get_time(),
                total_duration=media.get_duration(),
            )

        elif state == PAUSED_STATE:
            playback_status_display.update_status_string(
                state=PlaybackState.PAUSED,
                position=self.media_player.get_time(),
            )

        elif state == STOPPING_STATE:
            self.reset()
            send_exit("Playback stopped.")

        elif state == ENDED_STATE:
            current_idx = self.pm.current_idx
            playlist_length = self.pm.media_list.count()
            playback_mode = self.pc.playback_mode
            if current_idx == playlist_length - 1 and playback_mode == DEFAULT_PB_MODE:
                self.reset()
                send_exit("Playback ended.")
