import pygame

from mpy3.gui.widgets import Box, Button, Canvas


class App:
    def run(self) -> None:
        canvas = Canvas()
        play_button = Button("Play")
        pause_button = Button("Pause")
        container = Box(
            {
                "width": canvas.buffer.get_width(),
                "height": 60,
                "background_color": pygame.Color("gray"),
            }
        )
        canvas.add_widget(play_button)
        canvas.add_widget(pause_button)
        canvas.add_widget(container)

        pygame.init()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            canvas.update()

            pygame.display.flip()

        pygame.quit()
