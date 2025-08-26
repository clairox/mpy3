from typing import Literal, Optional, Self, TypedDict, Union

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


class Rectangle:
    def __init__(self, *args) -> None:
        if len(args) == 1:
            value = args[0]
            self.left = value
            self.right = value
            self.top = value
            self.bottom = value

        if len(args) == 4:
            self.left, self.right, self.top, self.bottom = args

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0, 0, 0)

    def __repr__(self) -> str:
        return f"Rectangle({self.left}, {self.right}, {self.top}, {self.bottom})"


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

        self.children: list[Widget] = []

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

        offset = Vector(0, 0)
        for widget in self.children:
            if isinstance(widget, Box):
                widget.draw(self, offset)
                offset.y += widget.get_height()

    def add_widget(self, widget: Widget) -> None:
        self.children.append(widget)


# ============================================================
#  Box
# ============================================================


class BoxProps(WidgetProps, total=False):
    width: float
    height: float

    border_size: int
    border_left_size: int
    border_right_size: int
    border_top_size: int
    border_bottom_size: int
    border_color: Color

    background_color: Color


class Box(Widget):
    def __init__(self, props: Optional[BoxProps] = None) -> None:
        super().__init__(props)

        self._class_name = "Box"
        self._generate_id(self._class_name)

        if props is None:
            props = {
                "width": 0,
                "height": 0,
                "border_size": 0,
                "border_color": colors["black"],
            }

        self.width = props.get("width") or 0
        self.height = props.get("height") or 0

        self.border_size = Rectangle(0)

        border_size_prop = props.get("border_size")
        if border_size_prop:
            self.border_size = Rectangle(border_size_prop)

        sides = ["left", "right", "top", "bottom"]

        for side in sides:
            prop = props.get(f"border_{side}_size")
            if prop:
                if side == "left":
                    self.border_size.left = prop
                elif side == "right":
                    self.border_size.right = prop
                elif side == "top":
                    self.border_size.top = prop
                elif side == "bottom":
                    self.border_size.bottom = prop

        self.border_color = props.get("border_color") or colors["black"]
        self.background_color = props.get("background_color") or None

        self.bounds = None

    def draw(self, canvas: Canvas, parent_offset: Vector) -> Rect:

        # If there is a border, self.bounds will be parent to Box inner content
        has_border = self.border_size != Rectangle.zero()

        total_children_height = sum(
            child.height for child in self.children if isinstance(child, Box)
        )

        if total_children_height > self.height:
            if has_border:
                self.height = (
                    total_children_height
                    + self.border_size.top
                    + self.border_size.bottom
                )
            else:
                self.height = total_children_height

        background_color = None
        if has_border:
            background_color = self.border_color
        else:
            background_color = self.background_color or canvas.background_color

        self.bounds = pygame.draw.rect(
            canvas.buffer,
            background_color,
            [parent_offset.x, parent_offset.y, self.width, self.height],
        )

        if not has_border:
            offset = Vector(self.bounds.left, self.bounds.right)
            self._draw_children(canvas, offset)
            return self.bounds

        # Box inner
        inner_x = parent_offset.x
        inner_y = parent_offset.y
        inner_width = self.width
        inner_height = self.height

        if self.border_size.left:
            size = self.border_size.left
            inner_width -= size
            inner_x += size

        if self.border_size.right:
            inner_width -= self.border_size.right

        if self.border_size.top:
            size = self.border_size.top
            inner_height -= size
            inner_y += size

        if self.border_size.bottom:
            inner_height -= self.border_size.bottom

        background_color = self.background_color or canvas.background_color

        inner_bounds = pygame.draw.rect(
            canvas.buffer,
            background_color,
            [inner_x, inner_y, inner_width, inner_height],
        )

        offset = Vector(inner_bounds.left, inner_bounds.top)
        self._draw_children(canvas, offset)

        return self.bounds

    def _draw_children(self, canvas: Canvas, offset: Vector):
        _offset = offset
        for child in [item for item in self.children if isinstance(item, Box)]:
            rect = child.draw(canvas, _offset)
            _offset.y += rect.height

    def add_widget(self, widget: Widget) -> None:
        self.children.append(widget)

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

    def draw(self, canvas: Canvas, parent_offset: Vector) -> Rect:
        self.bounds = super().draw(canvas, parent_offset)

        font = pygame.font.SysFont("Free Sans", 32)
        text = font.render(self.name, True, self.color)

        button_center = Vector(self.width / 2, self.height / 2)
        text_center = Vector(text.get_width() / 2, text.get_height() / 2)

        text_rel_pos_x = button_center.x - text_center.x
        text_rel_pos_y = button_center.y - text_center.y
        canvas.buffer.blit(
            text,
            [
                self.bounds.x + text_rel_pos_x,
                self.bounds.y + text_rel_pos_y,
            ],
        )

        return self.bounds
