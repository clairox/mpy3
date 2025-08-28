from collections import defaultdict
from threading import Event
from typing import Callable

from mpy3.gui.input_handler import InputEventName

EventName = InputEventName
EventCallback = Callable[[Event], None]


class EventDispatcher:
    def __init__(self):
        self._listeners: dict[EventName, list[EventCallback]] = defaultdict(list)

    def add_event_listener(self, event: EventName, callback: EventCallback) -> None:
        self._listeners[event].append(callback)

    def dispatch(self, event: EventName) -> None:
        for callback in list(self._listeners[event]):
            callback(Event())
