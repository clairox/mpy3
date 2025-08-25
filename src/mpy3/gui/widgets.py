from typing import NotRequired, Optional, Required, TypedDict

import pygame
from pygame import Color

from mpy3.gui.utils import generate_id

colors = {"black": Color("#000000"), "white": Color("#ffffff")}


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @classmethod
    def zero(cls):
        return Vector(0, 0)


class WidgetProps(TypedDict, total=False):
    position: NotRequired[Vector]


class Widget:
    def __init__(
        self,
        props: Optional[WidgetProps] = None,
    ):
        self._class_name = "Widget"
        self._generate_id(self._class_name)

        if props is None:
            props = {"position": Vector.zero()}

        self.position = props.get("position") or Vector.zero()

    def _generate_id(self, class_name: str):
        self.id = f"{class_name}_{generate_id()}" + generate_id()

    def set_position(self, value: Vector):
        self.position = value

    def set_pos_x(self, value: float):
        self.position = Vector(value, self.position.y)

    def set_pos_y(self, value: float):
        self.position = Vector(self.position.x, value)

    def get_position(self):
        return self.position


class BoxProps(WidgetProps, total=False):
    size: NotRequired[Vector]
    background_color: NotRequired[Color]


class Box(Widget):
    def __init__(self, props: Optional[BoxProps] = None):
        super().__init__(props)

        self._class_name = "Box"
        self._generate_id(self._class_name)

        if props is None:
            props = {
                "size": Vector.zero(),
                "position": Vector.zero(),
            }

        self.size = props.get("size") or Vector.zero()
        self.background_color = props.get("background_color") or None

    def set_size(self, value: Vector):
        self.size = value

    def set_width(self, value: float):
        self.size = Vector(value, self.size.y)

    def set_height(self, value: float):
        self.size = Vector(self.size.x, value)

    def get_size(self):
        return self.size

    def get_width(self):
        return self.size.x

    def get_height(self):
        return self.size.y


DEFAULT_BUTTON_SIZE = Vector(160, 70)


class ButtonProps(BoxProps, total=False):
    color: NotRequired[Color]


class Button(Box):
    def __init__(self, name: str, props: Optional[ButtonProps] = None):
        super().__init__(props)

        self._class_name = "Button"
        self._generate_id(self._class_name)

        self.name = name

        if props is None:
            props = {
                "size": DEFAULT_BUTTON_SIZE,
                "background_color": colors["black"],
                "color": colors["white"],
            }

        self.size = props.get("size") or DEFAULT_BUTTON_SIZE
        self.background_color = props.get("background_color") or colors["black"]
        self.color = props.get("color") or colors["white"]


class Screen:
    def __init__(self):
        self.screen = pygame.display.set_mode([1200, 700])
        self.background_color = colors["white"]
        self.widgets: list[Widget] = []

    def update(self):
        self.screen.fill(self.background_color)
        for widget in self.widgets:
            if type(widget) is Box:
                box = widget
                position = box.get_position()
                width = box.get_width()
                height = box.get_height()
                pygame.draw.rect(
                    self.screen,
                    box.background_color or self.background_color,
                    [position.x, position.y, width, height],
                )

            if type(widget) is Button:
                button = widget
                position = button.get_position()
                width = button.get_width()
                height = button.get_height()
                pygame.draw.rect(
                    self.screen,
                    button.background_color,
                    [position.x, position.y, width, height],
                )

                font = pygame.font.SysFont("Free Sans", 32)
                text = font.render(button.name, True, button.color)

                button_center = Vector(button.get_width() / 2, button.get_height() / 2)
                text_center = Vector(text.get_width() / 2, text.get_height() / 2)

                text_rel_pos_x = button_center.x - text_center.x
                text_rel_pos_y = button_center.y - text_center.y
                self.screen.blit(
                    text,
                    [
                        button.position.x + text_rel_pos_x,
                        button.position.y + text_rel_pos_y,
                    ],
                )

    def add_widget(self, widget: Widget):
        self.widgets.append(widget)
