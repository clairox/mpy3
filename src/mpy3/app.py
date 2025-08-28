from pathlib import Path

import pygame

from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen
from mpy3.views.home_page import HomePage


class App:
    def __init__(self, media_dir: Path) -> None:
        pygame.init()
        pygame.display.set_caption("mpy3")

        self.screen = Screen()
        self.canvas = Canvas(self.screen)
        self.clock = pygame.time.Clock()

        self.pages = {"home": HomePage}
        self._set_current_page("home", media_dir)

    def run(self) -> None:
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.update()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _set_current_page(self, key: str, *args) -> None:
        page = self.pages[key]
        content = page(self.screen, self.canvas, *args).render()
        self.canvas.add_widget(content)
