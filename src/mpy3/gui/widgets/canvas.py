from typing import Optional

from mpy3.gui.colors import colors
from mpy3.gui.widgets.box import Box, BoxProps
from mpy3.gui.widgets.screen import Screen


class CanvasProps(BoxProps, total=False):
    pass


class Canvas(Box):
    def __init__(self, screen: Screen, props: Optional[CanvasProps] = None) -> None:
        super().__init__(props)

        self.width = screen.buffer.get_width()
        self.height = screen.buffer.get_height()

        self.background_color = screen.background_color

        screen.add_widget(self)
