from typing import Literal, Optional, Self, TypedDict, Union, cast

import pygame
from pygame import Color, Rect

from mpy3.gui.utils import generate_id

colors = {"black": Color("#000000"), "white": Color("#ffffff")}


class Vector:
    def __init__(self, *args) -> None:
        if len(args) == 1:
            value = args[0]
            self.x = value
            self.y = value

        if len(args) == 2:
            self.x, self.y = args

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0)

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other: Self) -> Self:
        result = Vector(0)
        result.x = self.x + other.x
        result.y = self.y + other.y
        return cast(Self, result)


class Rectangle:
    def __init__(self, *args) -> None:
        if len(args) == 1:
            value = args[0]
            self._left = value
            self._right = value
            self._top = value
            self._bottom = value

        if len(args) == 4:
            self._left, self._right, self._top, self._bottom = args

        self._x = self._left + self._right
        self._y = self._top + self._bottom

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def top(self):
        return self._top

    @property
    def bottom(self):
        return self._bottom

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @left.setter
    def left(self, value: int) -> None:
        self._left = value
        self._x = self._left + self._right

    @right.setter
    def right(self, value: int) -> None:
        self._right = value
        self._x = self._left + self._right

    @top.setter
    def top(self, value: int) -> None:
        self._top = value
        self._y = self._top + self._bottom

    @bottom.setter
    def bottom(self, value: int) -> None:
        self._bottom = value
        self._y = self._top + self._bottom

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0, 0, 0)

    def __repr__(self) -> str:
        return f"Rectangle({self.left}, {self.right}, {self.top}, {self.bottom})"

    def __eq__(self, other: object) -> bool:
        other = cast(Rectangle, other)

        if (
            self.left == other.left
            and self.right == other.right
            and self.top == other.top
            and self.bottom == other.bottom
        ):
            return True

        return False


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
                widget.draw(self, offset, "start")
                offset.y += widget.get_height()

    def add_widget(self, widget: Widget) -> None:
        self.children.append(widget)


# ============================================================
#  Box
# ============================================================

Distribution = Union[
    Literal["start"], Literal["end"], Literal["center"], Literal["between"]
]

Alignment = Literal["start", "end", "center"]


class BoxProps(WidgetProps, total=False):
    distribution: Distribution
    child_alignment: Alignment

    padding: int
    padding_left: int
    padding_right: int
    padding_top: int
    padding_bottom: int

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
                "distribution": "center",
                "child_alignment": "start",
                "padding": 0,
                "width": 0,
                "height": 0,
                "border_size": 0,
                "border_color": colors["black"],
            }

        self.distribution = props.get("distribution") or "center"
        self.child_alignment = props.get("child_alignment") or "start"

        self.padding = Rectangle(0)
        padding_prop = props.get("padding")
        if padding_prop:
            self.padding = Rectangle(padding_prop)

        sides = ["left", "right", "top", "bottom"]

        for side in sides:
            prop = props.get(f"padding_{side}")
            if prop:
                if side == "left":
                    self.padding.left = prop
                elif side == "right":
                    self.padding.right = prop
                elif side == "top":
                    self.padding.top = prop
                elif side == "bottom":
                    self.padding.bottom = prop

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

    def draw(
        self, canvas: Canvas, parent_offset: Vector, alignment: Alignment = "start"
    ) -> Rect:
        offset = parent_offset

        self._resize_to_fit_children()

        if alignment == "center":
            parent_offset.y -= self.height / 2

        hierarchy = []

        has_border = self.border_size != Rectangle.zero()
        if has_border:
            border_bounds = self._draw_border(canvas, offset)
            offset = parent_offset + Vector(self.border_size.left, self.border_size.top)
            hierarchy.append(border_bounds)

        has_padding = self.padding != Rectangle.zero()
        if has_padding:
            padding_bounds = self._draw_padding(canvas, offset)
            offset = parent_offset + Vector(self.padding.left, self.padding.top)
            hierarchy.append(padding_bounds)

        content_bounds = self._draw_content(canvas, offset)
        offset = Vector(content_bounds.left, content_bounds.top)
        hierarchy.append(content_bounds)

        if self.child_alignment == "center":
            offset.y += content_bounds.height / 2

        self._draw_children(canvas, offset, cast(Alignment, self.child_alignment))

        self.bounds = hierarchy[0]
        return self.bounds

    def _resize_to_fit_children(self) -> None:
        total_children_width, total_children_height = [0, 0]
        box_children = [child for child in self.children if isinstance(child, Box)]
        total_children_width = sum(child.width for child in box_children)
        total_children_height = sum(child.height for child in box_children)

        content_width = self.width - self.border_size.x - self.padding.x
        content_height = self.height - self.border_size.y - self.padding.y
        if total_children_width > content_width:
            self.width = total_children_width + self.border_size.x + self.padding.x
        if total_children_height > content_height:
            self.height = total_children_height + self.border_size.y + self.padding.y

    def _draw_border(self, canvas: Canvas, parent_offset: Vector) -> Rect:
        background_color = self.border_color

        return pygame.draw.rect(
            canvas.buffer,
            background_color,
            [parent_offset.x, parent_offset.y, self.width, self.height],
        )

    def _draw_padding(self, canvas: Canvas, parent_offset: Vector):
        background_color = self.background_color or canvas.background_color

        width = self.width - self.border_size.x
        height = self.height - self.border_size.y

        return pygame.draw.rect(
            canvas.buffer,
            background_color,
            [parent_offset.x, parent_offset.y, width, height],
        )

    def _draw_content(self, canvas: Canvas, parent_offset: Vector) -> Rect:
        background_color = self.background_color or canvas.background_color

        offset_x = parent_offset.x
        offset_y = parent_offset.y
        width = self.width - self.border_size.x - self.padding.x
        height = self.height - self.border_size.y - self.padding.y

        return pygame.draw.rect(
            canvas.buffer,
            background_color,
            [offset_x, offset_y, width, height],
        )

    def _draw_children(
        self, canvas: Canvas, offset: Vector, alignment: Alignment = "start"
    ):
        _offset = offset
        for child in [item for item in self.children if isinstance(item, Box)]:
            rect = child.draw(canvas, _offset, alignment)
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
#  Text
# ============================================================

DEFAULT_FONT = "Free Sans"
DEFAULT_FONT_SIZE = 26


class TextProps(BoxProps, total=False):
    background_color: Color
    color: Color
    font: str
    font_size: int


class Text(Box):
    def __init__(self, value: str, props: Optional[TextProps] = None) -> None:
        super().__init__(props)

        self._class_name = "Text"
        self._generate_id(self._class_name)

        self.value = value

        font_name = props.get("font") or DEFAULT_FONT if props else DEFAULT_FONT
        font_size = (
            props.get("font_size") or DEFAULT_FONT_SIZE if props else DEFAULT_FONT_SIZE
        )
        font_color = props.get("color") or colors["black"] if props else colors["black"]
        font = pygame.font.SysFont(font_name, font_size)
        self.text = font.render(self.value, True, font_color)

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
        self, canvas: Canvas, parent_offset: Vector, alignment: Alignment = "start"
    ) -> Rect:
        self.bounds = super().draw(canvas, parent_offset, alignment)
        canvas.buffer.blit(self.text, [self.bounds.left, self.bounds.top])

        return self.bounds


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

    def draw(
        self, canvas: Canvas, parent_offset: Vector, alignment: Alignment = "start"
    ) -> Rect:
        self.bounds = super().draw(canvas, parent_offset, alignment)

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
