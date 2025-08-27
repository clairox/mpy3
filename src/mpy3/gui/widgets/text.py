from typing import Optional

import pygame
from pygame import Rect as PGRect

from mpy3.gui.colors import Colors
from mpy3.gui.widgets.box import DEFAULT_BOX_PROPS, Box, BoxProps, PartialBoxProps
from mpy3.gui.widgets.geometry import Vector
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.types import Alignment

DEFAULT_FONT = "Free Sans"
DEFAULT_FONT_SIZE = 26


class TextProps(BoxProps):
    color: str
    font_family: str
    font_size: int


class PartialTextProps(PartialBoxProps, total=False):
    color: str
    font_family: str
    font_size: int


DEFAULT_TEXT_PROPS: TextProps = {
    **DEFAULT_BOX_PROPS,
    "color": Colors.foreground,
    "font_family": "Free Sans",
    "font_size": 26,
}


class Text(Box):
    def __init__(self, value: str, props: Optional[PartialTextProps] = None) -> None:
        super().__init__(props)

        _props: TextProps = (
            DEFAULT_TEXT_PROPS if props is None else {**DEFAULT_TEXT_PROPS, **props}
        )

        self._class_name = "Text"
        self._generate_id(self._class_name)

        self.value = value

        self.font_family = _props["font_family"]
        self.font_size = _props["font_size"]
        self.color = _props["color"]
        self.background_color = _props["background_color"]

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
