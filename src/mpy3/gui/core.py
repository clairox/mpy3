import pygame

from mpy3.gui.widgets import Button, Screen, Vector


class App:
    def run(self):
        screen = Screen()
        play_button = Button("Play")
        pause_button = Button("Pause", {"position": Vector(200, 0)})
        screen.add_widget(play_button)
        screen.add_widget(pause_button)

        pygame.init()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.update()

            pygame.display.flip()

        pygame.quit()
