from mpy3.gui.widgets.canvas import Canvas
from mpy3.gui.widgets.screen import Screen
from mpy3.views.base import Page

RouteHandler = dict[str, type[Page]]


class Router:
    def __init__(self) -> None:
        self._routes: RouteHandler = {}
        self.current_route = None

    def init_router(self, screen: Screen, canvas: Canvas, routes: RouteHandler) -> None:
        self.screen = screen
        self.canvas = canvas
        self._routes: RouteHandler = routes
        self.goto("/")

    def goto(self, name: str, *args) -> None:
        if self.current_route is not None:
            self.current_route.cleanup()

        Route = self._routes[name]
        self.current_route = Route(self.screen, self.canvas, *args)


router = Router()
