import pygame

from mpy3.gui.colors import colors
from mpy3.gui.widgets.base import Widget
from mpy3.gui.widgets.box import Box
from mpy3.gui.widgets.geometry import Vector


class Canvas:
    def __init__(self) -> None:
        self.buffer = pygame.display.set_mode([1200, 700])
        self.background_color = colors["white"]
        self.children: list[Widget] = []

    def update(self) -> None:
        self.buffer.fill(self.background_color)

        offset = Vector(0, 0)
        for widget in self.children:
            if isinstance(widget, Box):
                widget.draw(self, offset, "start")
                offset.y += widget.get_height()

    def add_widget(self, widget: Widget) -> None:
        self.children.append(widget)
