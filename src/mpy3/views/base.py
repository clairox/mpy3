from mpy3.gui.widgets.box import Box
from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen


class Page:
    def __init__(self, screen: Screen, canvas: Canvas):
        self.screen = screen
        self.canvas = canvas

    def render(self) -> Box:
        return Box()
