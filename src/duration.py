"""
duration.py

This module contains the `Duration` class, which represents a duration in milliseconds
and provides methods to convert it to other time units such as seconds.
"""


class Duration:
    """
    A class to represent a duration in milliseconds and provide conversion methods.

    Args:
        ms (int): The duration in milliseconds.
    """

    def __init__(self, ms: int) -> None:
        self.ms = ms

    def to_millis(self) -> int:
        """
        Initializes a Duration instance with the given duration in milliseconds.

        Args:
            ms (int): The duration in milliseconds.
        """

        return self.ms

    def to_secs(self) -> int:
        """
        Converts the duration from milliseconds to seconds and returns it.

        Returns:
            int: The duration in seconds.
        """

        return self.ms // 1000
