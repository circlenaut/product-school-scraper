def format_seconds(seconds: float) -> str:
    """
    Convert seconds to a human-readable string in days, hours, minutes, and seconds.

    Args:
        seconds (float): The total number of seconds.

    Returns:
        str: A formatted string representing the time in days, hours, minutes, and seconds.
    """
    days, remainder = divmod(seconds, 86400)       # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)     # 3600 seconds in an hour
    minutes, secs = divmod(remainder, 60)          # 60 seconds in a minute

    parts = []
    if days >= 1:
        parts.append(f"{int(days)} day{'s' if days > 1 else ''}")
    if hours >= 1:
        parts.append(f"{int(hours)} hour{'s' if hours > 1 else ''}")
    if minutes >= 1:
        parts.append(f"{int(minutes)} minute{'s' if minutes > 1 else ''}")
    
    # Always append seconds
    parts.append(f"{secs:.2f} second{'s' if secs != 1 else ''}")

    return ", ".join(parts)