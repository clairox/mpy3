from typing import Protocol, cast

import pygame

from mpy3.gui.colors import Colors
from mpy3.gui.widgets.base import Widget
from mpy3.gui.widgets.geometry import Vector
from mpy3.gui.widgets.types import Alignment


class Screen:
    def __init__(self) -> None:
        self.buffer = pygame.display.set_mode([1200, 700])
        self.background_color = Colors.background
        self.children: list[Widget] = []

    def update(self) -> None:
        offset = Vector(0, 0)
        for widget in self.children:
            if hasattr(widget, "draw") and callable(getattr(widget, "draw")):
                box = cast(BoxLike, widget)
                box.draw(self, offset, "start")
                offset.y += box.get_height()

    def add_widget(self, widget: Widget) -> None:
        self.children.append(widget)


class BoxLike(Protocol):
    def draw(self, screen: Screen, offset: Vector, alignment: Alignment) -> None: ...
    def get_height(self) -> float: ...
