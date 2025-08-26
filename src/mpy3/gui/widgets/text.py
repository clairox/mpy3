from typing import Optional, cast

import pygame
from pygame import Color
from pygame import Rect as PGRect

from mpy3.gui.colors import colors
from mpy3.gui.widgets.box import Box, BoxProps
from mpy3.gui.widgets.geometry import Vector
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.types import Alignment

DEFAULT_FONT = "Free Sans"
DEFAULT_FONT_SIZE = 26


class TextProps(BoxProps, total=False):
    background_color: Color
    color: Color
    font_family: str
    font_size: int


class Text(Box):
    def __init__(self, value: str, props: Optional[TextProps] = None) -> None:
        super().__init__(props)

        self._class_name = "Text"
        self._generate_id(self._class_name)

        self.value = value

        self.font_family = (
            props.get("font_family") or DEFAULT_FONT if props else DEFAULT_FONT
        )
        self.font_size = (
            props.get("font_size") or DEFAULT_FONT_SIZE if props else DEFAULT_FONT_SIZE
        )
        self.font_color = (
            props.get("color") or colors["black"] if props else colors["black"]
        )

        self._render_text()

        defaults = {
            "width": self.text.get_width(),
            "height": self.text.get_height(),
            "background_color": colors["white"],
            "color": colors["black"],
        }

        if props is None:
            props = cast(TextProps, defaults)

        self.width = props.get("width") or defaults["width"]
        self.height = props.get("height") or defaults["height"]
        self.background_color = (
            props.get("background_color") or defaults["background_color"]
        )
        self.color = props.get("color") or defaults["color"]

    def draw(
        self, screen: Screen, parent_offset: Vector, alignment: Alignment = "start"
    ) -> PGRect:
        self.bounds = super().draw(screen, parent_offset, alignment)
        screen.buffer.blit(self.text, [self.bounds.left, self.bounds.top])

        return self.bounds

    def _render_text(self) -> None:
        font = pygame.font.SysFont(self.font_family, self.font_size)
        self.text = font.render(self.value, True, self.font_color)
        self.width = self.text.get_width()
        self.height = self.text.get_height()

    def set_value(self, value: str) -> None:
        self.value = value
        self._render_text()
