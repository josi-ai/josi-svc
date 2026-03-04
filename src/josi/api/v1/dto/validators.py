"""Shared validators for DTOs."""
import re
from datetime import time


def parse_birth_time(v: str) -> time:
    """Parse a flexible time string into a time object.

    Accepts HH:MM, HH:MM:SS, or HH:MM AM/PM formats.
    Raises ValueError if the format is invalid.
    """
    v = v.strip()

    # AM/PM format
    match = re.match(
        r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)$", v
    )
    if match:
        hour, minute, second, period = match.groups()
        hour, minute = int(hour), int(minute)
        second = int(second) if second else 0
        if period.upper() == "PM" and hour != 12:
            hour += 12
        elif period.upper() == "AM" and hour == 12:
            hour = 0
        return time(hour, minute, second)

    # 24-hour format
    match = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", v)
    if match:
        hour, minute, second = match.groups()
        hour, minute = int(hour), int(minute)
        second = int(second) if second else 0
        if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
            return time(hour, minute, second)

    raise ValueError(
        f"Invalid time format: {v}. Use HH:MM, HH:MM:SS, or HH:MM AM/PM"
    )
