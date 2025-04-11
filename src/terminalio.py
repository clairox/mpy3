"""
This module handles terminal io related function
"""

import sys
import termios
import tty

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)


def getch():
    """
    Capture and return input
    """

    try:
        tty.setraw(fd)
        first = sys.stdin.read(1)
        if first == "\x1b":
            rest = sys.stdin.read(2)
            return first + rest

        return first
    finally:
        reset_terminal()


def reset_terminal():
    """
    Set terminal attributes to original settings
    """

    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
