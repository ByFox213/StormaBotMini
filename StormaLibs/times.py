import time
from datetime import UTC, datetime

from nextcord.utils import format_dt


__all__ = (
    "seconds_to_hour",
    "seconds_to_time",
)


def seconds_to_hour(seconds: int) -> float:
    if seconds < 360:  # seconds < hour / 10
        return 0.0
    data = str(seconds / 3600)
    return float(data[:data.rfind(".")+2])


def seconds_to_time(seconds: int | float) -> str:
    x = time.gmtime(seconds)
    fr = "%H:%M:%S"
    if x.tm_mday > 1:
        fr = f"%D:%H:%M:%S"
    return time.strftime(fr, x)
