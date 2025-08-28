import pygame

from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen
from mpy3.router import router
from mpy3.views.home_page import HomePage
from mpy3.views.player_page import PlayerPage

pygame.init()
pygame.display.set_caption("mpy3")

screen = Screen()
canvas = Canvas(screen)
clock = pygame.time.Clock()


class App:
    def __init__(self) -> None:
        router.init_router(screen, canvas, {"/": HomePage, "/player": PlayerPage})

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self._render_current_page()
            screen.update()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def _render_current_page(self) -> None:
        if router.current_route is None:
            raise TypeError("Current route should not be None")

        page = router.current_route.render()

        canvas.clear()
        canvas.add_widget(page)
