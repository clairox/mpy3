from threading import Event

from mpy3.gui.colors import Colors
from mpy3.gui.widgets.box import Box
from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.text import Text
from mpy3.player import Media, MediaPlayer
from mpy3.utils import time_from_ms
from mpy3.views.base import Page


class PlayerPage(Page):
    def __init__(self, screen: Screen, canvas: Canvas, media: Media) -> None:
        super().__init__(screen, canvas)

        self.media = media
        self.media_player = MediaPlayer(self.media)
        self.media_player.play_until_done()

        self.screen.add_event_listener("onplay", self.handle_play)
        self.screen.add_event_listener("onstop", self.handle_stop)

    def handle_play(self, _: Event) -> None:
        if self.media_player.paused:
            self.media_player.play_until_done()
        else:
            self.media_player.pause()

    def handle_stop(self, _: Event) -> None:
        self.media_player.stop()

    def render(self) -> Box:
        container_widget = Box(
            {
                "orientation": "column",
                "spacing": 72,
                "padding": 18,
                "width": self.canvas.get_width(),
                "height": self.canvas.get_height(),
            }
        )

        meta = self.media.meta

        # Track Info
        track_info_widget = Box(
            {"orientation": "column", "spacing": 4, "padding_left": 2}
        )
        track_artist_widget = Text(
            meta["artist"] if meta else "Unknown Artist", {"font_size": 24}
        )
        track_title_widget = Text(self.media.title, {"font_size": 38})

        track_info_widget.add_widget(track_artist_widget)
        track_info_widget.add_widget(track_title_widget)

        # Track Progress
        time_elapsed = self.media_player.get_time()
        track_duration = self.media.duration

        time_container = Box({"spacing": 8, "padding_left": 2})
        time_elapsed_widget = Text(time_from_ms(time_elapsed), {"font_size": 26})
        slash_widget = Text("/", {"font_size": 26})
        track_duration_widget = Text(time_from_ms(track_duration), {"font_size": 26})

        time_container.add_widget(time_elapsed_widget)
        time_container.add_widget(slash_widget)
        time_container.add_widget(track_duration_widget)

        progress = time_elapsed / track_duration

        track_progress_container = Box(
            {
                "orientation": "column",
                "spacing": 8,
                "width": container_widget.get_width()
                - container_widget.padding.left
                - container_widget.padding.right,
                "height": 20,
            }
        )
        track_progress = Box(
            {
                "width": track_progress_container.get_width() * progress,
                "height": track_progress_container.get_height(),
                "background_color": Colors.black,
            }
        )

        track_progress_container.add_widget(time_container)
        track_progress_container.add_widget(track_progress)

        container_widget.add_widget(track_info_widget)
        container_widget.add_widget(track_progress_container)

        return container_widget

    def cleanup(self) -> None:
        self.screen.remove_event_listener("onplay", self.handle_play)
        self.screen.remove_event_listener("onstop", self.handle_stop)
