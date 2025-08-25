from typing import Optional, Self, TypedDict

import pygame
from pygame import Color, Rect

from mpy3.gui.utils import generate_id

colors = {"black": Color("#000000"), "white": Color("#ffffff")}


class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0)

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

# ============================================================
#  Widget
# ============================================================


class WidgetProps(TypedDict, total=False):
    pass


class Widget:
    def __init__(
        self,
        props: Optional[WidgetProps] = None,
    ) -> None:
        self._class_name = "Widget"
        self._generate_id(self._class_name)

        if props is None:
            props = {}

    def _generate_id(self, class_name: str) -> None:
        self.id = f"{class_name}_{generate_id()}" + generate_id()


# ============================================================
#  Canvas
# ============================================================


class Canvas:
    def __init__(self) -> None:
        self.buffer = pygame.display.set_mode([1200, 700])
        self.background_color = colors["white"]
        self.children: list[Widget] = []

    def update(self) -> None:
        self.buffer.fill(self.background_color)

        offset = 0
        for widget in self.children:
            if isinstance(widget, Box):
                widget.draw(self, offset)
                offset += widget.get_height()

    def add_widget(self, widget: Widget) -> None:
        self.children.append(widget)


# ============================================================
#  Box
# ============================================================


class BoxProps(WidgetProps, total=False):
    width: float
    height: float
    background_color: Color


class Box(Widget):
    def __init__(self, props: Optional[BoxProps] = None) -> None:
        super().__init__(props)

        self._class_name = "Box"
        self._generate_id(self._class_name)

        if props is None:
            props = {"width": 0, "height": 0}

        self.width = props.get("width") or 0
        self.height = props.get("height") or 0
        self.background_color = props.get("background_color") or None

    def draw(self, canvas: Canvas, offset) -> Rect:
        return pygame.draw.rect(
            canvas.buffer,
            self.background_color or canvas.background_color,
            [0, offset, self.width, self.height],
        )

    def set_width(self, value: float) -> None:
        self.width = value

    def set_height(self, value: float) -> None:
        self.height = value

    def get_width(self) -> float:
        return self.width

    def get_height(self) -> float:
        return self.height


# ============================================================
#  Button
# ============================================================


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

    def draw(self, canvas: Canvas, offset) -> Rect:
        rect = super().draw(canvas, offset)

        font = pygame.font.SysFont("Free Sans", 32)
        text = font.render(self.name, True, self.color)

        button_center = Vector(self.width / 2, self.height / 2)
        text_center = Vector(text.get_width() / 2, text.get_height() / 2)

        text_rel_pos_x = button_center.x - text_center.x
        text_rel_pos_y = button_center.y - text_center.y
        canvas.buffer.blit(
            text,
            [
                rect.x + text_rel_pos_x,
                rect.y + text_rel_pos_y,
            ],
        )

        return rect
