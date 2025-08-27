from dataclasses import dataclass, field
from typing import Optional, Self, cast

import pygame
from pygame import Rect as PGRect
from pygame.color import Color

from mpy3.gui.colors import Colors
from mpy3.gui.widgets.base import Widget, WidgetProps
from mpy3.gui.widgets.geometry import Rectangle, Vector
from mpy3.gui.widgets.screen import Screen
from mpy3.gui.widgets.types import Alignment, Distribution


@dataclass
class BoxProps(WidgetProps):
    distribution: Distribution = "center"
    child_alignment: Alignment = "start"
    spacing: int = 0

    padding: int = 0
    padding_left: int = 0
    padding_right: int = 0
    padding_top: int = 0
    padding_bottom: int = 0
    padding_horizontal: int = 0
    padding_vertical: int = 0

    width: float = 0
    height: float = 0

    border_size: int = 0
    border_left_size: int = 0
    border_right_size: int = 0
    border_top_size: int = 0
    border_bottom_size: int = 0
    border_color: str = Colors.foreground

    background_color: str = Colors.background


class Box(Widget):
    def __init__(self, props: Optional[BoxProps] = None) -> None:
        props = self._init_props(BoxProps, props)
        super().__init__(props)

        self._class_name = "Box"
        self._generate_id(self._class_name)

        self.distribution = props.distribution
        self.child_alignment = props.child_alignment
        self.spacing = props.spacing
        self.width = props.width
        self.height = props.height
        self.border_color = props.border_color
        self.background_color = props.background_color

        self.padding = Rectangle(0)
        padding_prop = props.padding
        if padding_prop:
            self.padding = Rectangle(padding_prop)

        sides = ["left", "right", "top", "bottom", "horizontal", "vertical"]

        for side in sides:
            prop = props[f"padding_{side}"]
            if prop:
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
        border_size_prop = props.border_size
        if border_size_prop:
            self.border_size = Rectangle(border_size_prop)

        sides = ["left", "right", "top", "bottom"]

        for side in sides:
            prop = props[f"border_{side}_size"]
            if prop:
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
