from pathlib import Path

import pygame

from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen
from mpy3.views.home_page import HomePage


class App:
    def __init__(self, media_dir: Path) -> None:
        pygame.init()
        pygame.display.set_caption("mpy3")

        self.media_dir = media_dir

        self.screen = Screen()
        self.canvas = Canvas(self.screen)
        self.clock = pygame.time.Clock()

        self.pages = {"home": HomePage}

    def run(self) -> None:
        self._set_current_page("home", self.media_dir)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self._render_current_page()
            self.screen.update()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _set_current_page(self, key: str, *args) -> None:
        Page = self.pages[key]
        self.current_page = Page(self.screen, self.canvas, *args)

    def _render_current_page(self) -> None:
        content = self.current_page.render()
        self.canvas.clear()
        self.canvas.add_widget(content)
