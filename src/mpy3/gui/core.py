import pygame

from mpy3.gui.widgets import Box, Button, Screen, Vector


class App:
    def run(self):
        screen = Screen()
        play_button = Button("Play")
        pause_button = Button("Pause")
        container = Box(
            {
                "size": Vector(screen.screen.get_width(), 60),
                "background_color": pygame.Color("#000000"),
            }
        )
        screen.add_widget(play_button)
        screen.add_widget(pause_button)
        screen.add_widget(container)

        pygame.init()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.update()

            pygame.display.flip()

        pygame.quit()
