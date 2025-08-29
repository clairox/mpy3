from typing import Callable, Literal

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

InputEventName = Literal["onplay", "onstop", "onright", "onleft", "ondown", "onup"]

KEY_EVENTS: dict[Key | str, InputEventName] = {
    Key.space: "onplay",
    Key.backspace: "onstop",
    Key.right: "onright",
    Key.left: "onleft",
    Key.down: "ondown",
    Key.up: "onup",
    #
    "h": "onleft",
    "j": "ondown",
    "k": "onup",
    "l": "onright",
    #
    "w": "onup",
    "a": "onleft",
    "s": "ondown",
    "d": "onright",
}


class InputHandler:
    def __init__(self, dispatch: Callable[[InputEventName], None]) -> None:
        self.dispatch = dispatch

        listener = keyboard.Listener(on_press=self._handle_press)
        listener.start()
        listener.stop

    def _handle_press(self, key: Key | KeyCode | None) -> None:
        value = key if isinstance(key, Key) else key.char if key is not None else None
        if value is None or value not in KEY_EVENTS:
            return

        self.dispatch(KEY_EVENTS[value])
