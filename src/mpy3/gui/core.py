from pathlib import Path

import pygame

from mpy3.gui.widgets.box import Box
from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.text import Text
from mpy3.player import Media


class App:
    def __init__(self, media_dir: Path):
        self.media_dir = media_dir

        unsorted_media_list: list[Media] = []
        for mrl in self.media_dir.iterdir():
            media = Media(mrl)
            media.parse_meta()
            unsorted_media_list.append(media)

        self.media_list = sorted(unsorted_media_list, key=lambda media: media.title)

    def run(self) -> None:
        pygame.init()
        screen = Screen()
        canvas = Canvas(screen)
        clock = pygame.time.Clock()

        if len(self.media_list) == 0:
            canvas.add_widget(Text("No music"))
        else:
            track_list_container = Box({"width": canvas.get_width()})

            for media in self.media_list:
                track_list_item = Box(
                    {
                        "child_alignment": "center",
                        "spacing": 6,
                        "padding_left": 14,
                        "padding_top": 10,
                        "padding_bottom": 10,
                        "width": track_list_container.get_width(),
                        "border_bottom_size": 2,
                    }
                )

                track_title = Text(media.title)
                track_artist = Text("Unknown artist", {"font_size": 20})
                if media.meta and media.meta["artist"]:
                    track_artist.set_value(media.meta["artist"])

                track_list_item.add_widget(track_title)
                track_list_item.add_widget(track_artist)
                track_list_container.add_widget(track_list_item)

            canvas.add_widget(track_list_container)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.update()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
