import atexit
import signal
import sys
import termios
import threading
import tty
from enum import Enum
from typing import Callable, cast


class Key(Enum):
    Q = 0
    SPACE = 1
    RIGHT = 2
    LEFT = 3
    NULL = 4


KEYMAP = {
    "q": Key.Q,
    " ": Key.SPACE,
    "\x1b[D": Key.RIGHT,
    "\x1b[C": Key.LEFT,
}


class KeyboardListener:
    def __init__(self) -> None:
        self._reader = InputReader()
        self._thread: threading.Thread | None = None

    def listen(self, callback: Callable[[Key], None]) -> None:
        self._thread = threading.Thread(target=self._run, args=[callback], daemon=True)
        self._thread.start()

    def _run(self, callback: Callable[[Key], None]) -> None:
        last_char = "\0"
        while last_char != "q":
            key = self._get_key_event()
            if key in cast(list[str], KEYMAP.keys()):
                last_char = key
                callback(self._process_key(key))

    def _process_key(self, key: str) -> Key:
        return KEYMAP.get(key, Key.NULL)

    def _get_key_event(self) -> str | None:
        return self._reader.read_key()


class InputReader:
    def __init__(self) -> None:
        self._fd = sys.stdin.fileno()
        self._old_settings = termios.tcgetattr(self._fd)
        self._reading = False

        atexit.register(lambda: self._disable_cbreak())
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda s, f: (self._disable_cbreak(), sys.exit(1)))

    def read_key(self) -> str | None:
        try:
            self._enable_cbreak()

            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch += sys.stdin.read(2)
            sys.stdout.write("\r")
            sys.stdout.flush()

            return ch
        except KeyboardInterrupt:
            pass
        finally:
            self._disable_cbreak()

    def _enable_cbreak(self) -> None:
        tty.setcbreak(self._fd)
        self._reading = True

    def _disable_cbreak(self) -> None:
        if self._old_settings is not None and self._reading:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)
            self._reading = False
