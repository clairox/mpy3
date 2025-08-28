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
