from typing import Optional, Self, cast

import pygame
from pygame import Rect as PGRect

from mpy3.gui.colors import Colors
from mpy3.gui.widgets.base import (
    DEFAULT_WIDGET_PROPS,
    PartialWidgetProps,
    Widget,
    WidgetProps,
)
from mpy3.gui.widgets.geometry import Rectangle, Vector
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.types import Alignment, Distribution

NAME = "Box"


class BoxProps(WidgetProps):
    distribution: Distribution
    child_alignment: Alignment
    spacing: int

    padding: int
    padding_left: int | None
    padding_right: int | None
    padding_top: int | None
    padding_bottom: int | None
    padding_horizontal: int | None
    padding_vertical: int | None

    width: float
    height: float

    border_size: int
    border_left_size: int | None
    border_right_size: int | None
    border_top_size: int | None
    border_bottom_size: int | None
    border_color: str

    background_color: str


class PartialBoxProps(PartialWidgetProps, total=False):
    distribution: Distribution
    child_alignment: Alignment
    spacing: int

    padding: int
    padding_left: int | None
    padding_right: int | None
    padding_top: int | None
    padding_bottom: int | None
    padding_horizontal: int | None
    padding_vertical: int | None

    width: float
    height: float

    border_size: int
    border_left_size: int | None
    border_right_size: int | None
    border_top_size: int | None
    border_bottom_size: int | None
    border_color: str

    background_color: str


DEFAULT_BOX_PROPS: BoxProps = {
    **DEFAULT_WIDGET_PROPS,
    "distribution": "center",
    "child_alignment": "start",
    "spacing": 0,
    "padding": 0,
    "padding_left": None,
    "padding_right": None,
    "padding_top": None,
    "padding_bottom": None,
    "padding_horizontal": None,
    "padding_vertical": None,
    "width": 0,
    "height": 0,
    "border_size": 0,
    "border_left_size": None,
    "border_right_size": None,
    "border_top_size": None,
    "border_bottom_size": None,
    "border_color": Colors.foreground,
    "background_color": Colors.background,
}


class Box(Widget):
    def __init__(self, props: Optional[PartialBoxProps] = None) -> None:
        super().__init__(props)

        _props: BoxProps = (
            DEFAULT_BOX_PROPS if props is None else {**DEFAULT_BOX_PROPS, **props}
        )

        self._generate_id(NAME)

        self.distribution = _props["distribution"]
        self.child_alignment = _props["child_alignment"]
        self.spacing = _props["spacing"]
        self.width = _props["width"]
        self.height = _props["height"]
        self.border_color = _props["border_color"]
        self.background_color = _props["background_color"]

        self.padding = Rectangle(0)
        padding_prop = _props["padding"]
        if padding_prop:
            self.padding = Rectangle(padding_prop)

        sides = ["left", "right", "top", "bottom", "horizontal", "vertical"]

        for side in sides:
            prop = _props[f"padding_{side}"]
            if prop is not None:
                if side == "left":
                    self.padding.left = prop
                elif side == "right":
                    self.padding.right = prop
                elif side == "top":
                    self.padding.top = prop
                elif side == "bottom":
                    self.padding.bottom = prop
                elif side == "horizontal":
                    self.padding.left = prop
                    self.padding.right = prop
                elif side == "vertical":
                    self.padding.top = prop
                    self.padding.bottom = prop

        self.border_size = Rectangle(0)
        border_size_prop = _props["border_size"]
        if border_size_prop:
            self.border_size = Rectangle(border_size_prop)

        sides = ["left", "right", "top", "bottom"]

        for side in sides:
            prop = _props[f"border_{side}_size"]
            if prop is not None:
                if side == "left":
                    self.border_size.left = prop
                elif side == "right":
                    self.border_size.right = prop
                elif side == "top":
                    self.border_size.top = prop
                elif side == "bottom":
                    self.border_size.bottom = prop

        self.bounds = None

    def draw(
        self, screen: Screen, parent_offset: Vector, alignment: Alignment = "start"
    ) -> PGRect:
        offset = parent_offset

        children_width, children_height = self._calculate_children_dimensions()
        self._resize_to_fit_dimensions(children_width, children_height)

        hierarchy = []

        has_border = self.border_size != Rectangle.zero()
        if has_border:
            border_bounds = self._draw_border(screen, offset)
            offset += Vector(self.border_size.left, self.border_size.top)
            hierarchy.append(border_bounds)

        has_padding = self.padding != Rectangle.zero()
        if has_padding:
            padding_bounds = self._draw_padding(screen, offset)
            offset += Vector(self.padding.left, self.padding.top)
            hierarchy.append(padding_bounds)

        content_bounds = self._draw_content(screen, offset)
        offset = Vector(content_bounds.left, content_bounds.top)
        hierarchy.append(content_bounds)

        if self.child_alignment == "center":
            offset.y += content_bounds.height / 2 - children_height / 2

        self._draw_children(screen, offset, cast(Alignment, self.child_alignment))

        self.bounds = hierarchy[0]
        return self.bounds

    def _resize_to_fit_dimensions(self, width: float, height: float) -> None:
        content_width = self.width - self.border_size.x - self.padding.x
        content_height = self.height - self.border_size.y - self.padding.y

        if width > content_width:
            self.width = width + self.border_size.x + self.padding.x

        if height > content_height:
            self.height = height + self.border_size.y + self.padding.y

    def _draw_border(self, screen: Screen, parent_offset: Vector) -> PGRect:
        background_color = self.border_color

        return pygame.draw.rect(
            screen.buffer,
            background_color,
            [parent_offset.x, parent_offset.y, self.width, self.height],
        )

    def _draw_padding(self, screen: Screen, parent_offset: Vector):
        background_color = self.background_color or screen.background_color
        background_color = Colors.background

        width = self.width - self.border_size.x
        height = self.height - self.border_size.y

        return pygame.draw.rect(
            screen.buffer,
            background_color,
            [parent_offset.x, parent_offset.y, width, height],
        )

    def _draw_content(self, screen: Screen, parent_offset: Vector) -> PGRect:
        background_color = self.background_color or screen.background_color

        offset_x = parent_offset.x
        offset_y = parent_offset.y
        width = self.width - self.border_size.x - self.padding.x
        height = self.height - self.border_size.y - self.padding.y

        return pygame.draw.rect(
            screen.buffer,
            background_color,
            [offset_x, offset_y, width, height],
        )

    def _draw_children(
        self, screen: Screen, offset: Vector, alignment: Alignment = "start"
    ):
        _offset = offset
        rendered_children = self._get_renderable_children()
        for i, child in enumerate(rendered_children):
            rect = child.draw(screen, _offset, alignment)
            _offset.y += rect.height

            if i < len(rendered_children) - 1:
                _offset.y += self.spacing

    def _get_renderable_children(self) -> list[Self]:
        return [cast(Self, child) for child in self.children if isinstance(child, Box)]

    def _calculate_children_dimensions(self) -> list[float]:
        rendered_children = self._get_renderable_children()
        spacing_size = self.spacing * (len(rendered_children) - 1)
        width = sum(child.width for child in rendered_children) + spacing_size
        height = sum(child.height for child in rendered_children) + spacing_size

        return [width, height]

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
