import os
from pathlib import Path

import pygame

from mpy3.gui.widgets import Box, Button, Canvas, Text
from mpy3.player import Media


class App:
    def __init__(self, media_dir: Path):
        self.media_dir = media_dir

        unsorted_media_list = []
        for mrl in self.media_dir.iterdir():
            media = Media(mrl)
            media.parse_meta()
            unsorted_media_list.append(media)

        self.media_list = sorted(unsorted_media_list, key=lambda media: media.title)

    def run(self) -> None:
        pygame.init()
        canvas = Canvas()
        clock = pygame.time.Clock()

        if len(self.media_list) == 0:
            canvas.add_widget(Text("No music"))
        else:
            track_list_container = Box({"width": canvas.buffer.get_width()})

            for media in self.media_list:
                label = ""
                if media.meta:
                    label = f'{media.title} - {media.meta["artist"]}'
                else:
                    label = media.title

                track_list_item = Box(
                    {
                        "child_alignment": "center",
                        "width": track_list_container.get_width(),
                        "height": 64,
                        "border_bottom_size": 2,
                    }
                )

                track_list_item_text = Text(label)
                track_list_item.add_widget(track_list_item_text)
                track_list_container.add_widget(track_list_item)

            canvas.add_widget(track_list_container)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            canvas.update()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
