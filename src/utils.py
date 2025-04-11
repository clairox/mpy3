"""
Utility functions
"""

import os
import sys


def log(*values: object) -> None:
    """
    Log and overwrite a single line to console
    """

    sys.stdout.write("\r\033[2K")
    sys.stdout.write(" ".join(str(v) for v in values))
    sys.stdout.flush()


def send_exit(status) -> None:
    """
    Exit app and log a status message to console
    """

    sys.stdout.write(status)
    sys.stdout.flush()
    os._exit(0)


def time_from_ms(ms: int) -> str:
    """
    Converts a time duration in milliseconds to a human-readable string format.

    Args:
        ms (int): The time duration in milliseconds.

    Returns:
        str: A string representing the time in the format "hh:mm:ss" if hours are present,
             or "mm:ss" if no hours are involved.

    Example:
        time_from_ms(3600000)  # Returns "1:00:00"
        time_from_ms(75000)    # Returns "1:15"
    """

    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"

    return f"{minutes}:{seconds:02}"
