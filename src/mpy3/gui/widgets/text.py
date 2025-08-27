from dataclasses import dataclass, field
from typing import Any, Optional

import pygame
from pygame import Color
from pygame import Rect as PGRect

from mpy3.gui.colors import Colors
from mpy3.gui.widgets.box import Box, BoxProps
from mpy3.gui.widgets.geometry import Vector
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.types import Alignment

DEFAULT_FONT = "Free Sans"
DEFAULT_FONT_SIZE = 26


@dataclass
class TextProps(BoxProps):
    background_color: str = Colors.background
    color: str = Colors.foreground
    font_family: str = DEFAULT_FONT
    font_size: int = DEFAULT_FONT_SIZE


class Text(Box):
    def __init__(
        self, value: str, props: Optional[TextProps | dict[str, Any]] = None
    ) -> None:
        props = self._init_props(TextProps, props)
        super().__init__(props)

        self._class_name = "Text"
        self._generate_id(self._class_name)

        self.value = value

        self.font_family = props.font_family
        self.font_size = props.font_size
        self.color = props.color
        self.background_color = props.background_color

        self._render_text()

    def draw(
        self, screen: Screen, parent_offset: Vector, alignment: Alignment = "start"
    ) -> PGRect:
        self.bounds = super().draw(screen, parent_offset, alignment)
        screen.buffer.blit(self.text, [self.bounds.left, self.bounds.top])

        return self.bounds

    def _render_text(self) -> None:
        font = pygame.font.SysFont(self.font_family, self.font_size)
        self.text = font.render(self.value, True, self.color)
        self.width = self.text.get_width()
        self.height = self.text.get_height()

    def set_value(self, value: str) -> None:
        self.value = value
        self._render_text()
