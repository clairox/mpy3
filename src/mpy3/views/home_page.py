from pathlib import Path

from mpy3.gui.widgets.box import Box
from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.text import Text
from mpy3.player import Media
from mpy3.views.base import Page


class HomePage(Page):
    def __init__(self, screen: Screen, canvas: Canvas, media_dir: Path) -> None:
        super().__init__(screen, canvas)

        self.media_dir = media_dir

        unsorted_media_list: list[Media] = []
        for mrl in self.media_dir.iterdir():
            media = Media(mrl)
            media.parse_meta()
            unsorted_media_list.append(media)

        self.media_list = sorted(unsorted_media_list, key=lambda media: media.title)

    def render(self) -> Box:
        container = Box(
            {"width": self.canvas.get_width(), "height": self.canvas.get_height()}
        )

        if len(self.media_list) == 0:
            container.add_widget(Text("No music"))
        else:
            track_list = Box({"width": container.get_width()})

            for media in self.media_list:
                track_list_item = Box(
                    {
                        "child_alignment": "center",
                        "spacing": 6,
                        "padding_horizontal": 18,
                        "padding_vertical": 14,
                        "width": track_list.get_width(),
                        "border_bottom_size": 2,
                    }
                )

                track_title = Text(media.title)
                track_artist = Text("Unknown artist", {"font_size": 20})
                if media.meta and media.meta["artist"]:
                    track_artist.set_value(media.meta["artist"])

                track_list_item.add_widget(track_title)
                track_list_item.add_widget(track_artist)

                track_list.add_widget(track_list_item)

            container.add_widget(track_list)

        return container
