from typing import Optional

import pygame
from pygame import Color
from pygame import Rect as PGRect

from mpy3.gui.colors import colors
from mpy3.gui.widgets.box import Box, BoxProps
from mpy3.gui.widgets.geometry import Vector
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.types import Alignment

DEFAULT_BUTTON_SIZE = Vector(160, 70)


class ButtonProps(BoxProps, total=False):
    color: Color


class Button(Box):
    def __init__(self, name: str, props: Optional[ButtonProps] = None) -> None:
        super().__init__(props)

        self._class_name = "Button"
        self._generate_id(self._class_name)

        self.name = name

        if props is None:
            props = {
                "width": DEFAULT_BUTTON_SIZE.x,
                "height": DEFAULT_BUTTON_SIZE.y,
                "background_color": colors["black"],
                "color": colors["white"],
            }

        self.width = props.get("width") or DEFAULT_BUTTON_SIZE.x
        self.height = props.get("height") or DEFAULT_BUTTON_SIZE.y
        self.background_color = props.get("background_color") or colors["black"]
        self.color = props.get("color") or colors["white"]

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
