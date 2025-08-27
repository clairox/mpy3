from typing import Optional

from mpy3.gui.widgets.box import DEFAULT_BOX_PROPS, Box, BoxProps, PartialBoxProps
from mpy3.gui.widgets.screen import Screen

NAME = "Canvas"


class CanvasProps(BoxProps):
    pass


class PartialCanvasProps(PartialBoxProps, total=False):
    pass


DEFAULT_CANVAS_PROPS: CanvasProps = {**DEFAULT_BOX_PROPS}


class Canvas(Box):
    def __init__(
        self, screen: Screen, props: Optional[PartialCanvasProps] = None
    ) -> None:
        super().__init__(props)

        # _props: CanvasProps = (
        #     DEFAULT_CANVAS_PROPS if props is None else {**DEFAULT_CANVAS_PROPS, **props}
        # )

        self._generate_id(NAME)

        self.width = screen.buffer.get_width()
        self.height = screen.buffer.get_height()

        self.background_color = screen.background_color

        screen.add_widget(self)
