from pathlib import Path
from threading import Event

from mpy3.gui.colors import Colors
from mpy3.gui.widgets.box import Box
from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.text import Text
from mpy3.player import Media
from mpy3.router import router
from mpy3.views.base import Page

DEFAULT_MEDIA_DIR = Path.home() / "mpy3/tracks/"


class HomePage(Page):
    def __init__(self, screen: Screen, canvas: Canvas) -> None:
        super().__init__(screen, canvas)

        self.media_dir = Path(DEFAULT_MEDIA_DIR)
        if not self.media_dir.exists():
            Path.mkdir(self.media_dir, parents=True)

        unsorted_media_list: list[Media] = []
        for mrl in self.media_dir.iterdir():
            media = Media(mrl)
            media.parse_meta()
            unsorted_media_list.append(media)

        self.media_list = sorted(unsorted_media_list, key=lambda media: media.title)

        self.screen.add_event_listener("onplay", self.handle_play)
        self.screen.add_event_listener("ondown", self.handle_down)
        self.screen.add_event_listener("onup", self.handle_up)

        self.index = 0

    def handle_play(self, _: Event) -> None:
        media = self.media_list[self.index]
        router.goto("/player", media)

    def handle_down(self, _: Event) -> None:
        next_index = self.index + 1
        self.index = 0 if next_index == len(self.media_list) else next_index

    def handle_up(self, _: Event) -> None:
        next_index = self.index - 1
        self.index = len(self.media_list) - 1 if next_index < 0 else next_index

    def render(self) -> Box:
        container = Box(
            {
                "orientation": "column",
                "width": self.canvas.get_width(),
                "height": self.canvas.get_height(),
            }
        )

        if len(self.media_list) == 0:
            container.add_widget(Text("No music"))
        else:
            track_list = Box({"orientation": "column", "width": container.get_width()})

            for i, media in enumerate(self.media_list):
                background_color = Colors.black if i == self.index else Colors.white
                text_color = Colors.white if i == self.index else Colors.black

                track_list_item = Box(
                    {
                        "orientation": "column",
                        "child_alignment": "center",
                        "spacing": 6,
                        "padding_horizontal": 18,
                        "padding_vertical": 14,
                        "width": track_list.get_width(),
                        "border_bottom_size": 2,
                        "background_color": background_color,
                    }
                )

                track_title = Text(
                    media.title,
                    {"color": text_color, "background_color": background_color},
                )
                track_artist = Text(
                    "Unknown artist",
                    {
                        "font_size": 20,
                        "color": text_color,
                        "background_color": background_color,
                    },
                )
                if media.meta and media.meta["artist"]:
                    track_artist.set_value(media.meta["artist"])

                track_list_item.add_widget(track_title)
                track_list_item.add_widget(track_artist)

                track_list.add_widget(track_list_item)

            container.add_widget(track_list)

        return container
