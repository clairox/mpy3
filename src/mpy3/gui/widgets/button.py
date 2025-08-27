from typing import Optional

import pygame
from pygame import Rect as PGRect

from mpy3.gui.colors import Colors
from mpy3.gui.widgets.box import DEFAULT_BOX_PROPS, Box, BoxProps, PartialBoxProps
from mpy3.gui.widgets.geometry import Vector
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.types import Alignment

DEFAULT_BUTTON_SIZE = Vector(160, 70)


class ButtonProps(BoxProps):
    color: str


class PartialButtonProps(PartialBoxProps, total=False):
    color: str


DEFAULT_BUTTON_PROPS: ButtonProps = {
    **DEFAULT_BOX_PROPS,
    "background_color": Colors.black,
    "color": Colors.white,
}


class Button(Box):
    def __init__(self, name: str, props: Optional[PartialButtonProps] = None) -> None:
        super().__init__(props)

        _props: ButtonProps = (
            DEFAULT_BUTTON_PROPS if props is None else {**DEFAULT_BUTTON_PROPS, **props}
        )

        self._class_name = "Button"
        self._generate_id(self._class_name)

        self.name = name

        self.width = _props["width"]
        self.height = _props["height"]
        self.background_color = _props["background_color"]
        self.color = _props["color"]

    def draw(
        self, screen: Screen, parent_offset: Vector, alignment: Alignment = "start"
    ) -> PGRect:
        self.bounds = super().draw(screen, parent_offset, alignment)

        font = pygame.font.SysFont("Free Sans", 32)
        text = font.render(self.name, True, self.color)

        button_center = Vector(self.width / 2, self.height / 2)
        text_center = Vector(text.get_width() / 2, text.get_height() / 2)

        text_rel_pos_x = button_center.x - text_center.x
        text_rel_pos_y = button_center.y - text_center.y
        screen.buffer.blit(
            text,
            [
                self.bounds.x + text_rel_pos_x,
                self.bounds.y + text_rel_pos_y,
            ],
        )

        return self.bounds
