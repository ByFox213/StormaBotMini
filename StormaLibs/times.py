import time
from datetime import UTC, datetime

from nextcord.utils import format_dt

hour = 3600


__all__ = (
    "seconds_to_hour",
    "seconds_to_time",
    "format_dt_"
)


def seconds_to_hour(seconds: int) -> float:
    if seconds < 360:                 # seconds < hour / 10
        return 0.0
    data = str(seconds / hour)
    t = 0
    for i in data:
        t += 1
        if i == '.':
            return float(data[:t+1])


def seconds_to_time(seconds: int | float) -> str:
    x = time.gmtime(seconds)
    fr = "%H:%M:%S"
    if x.tm_mday > 1:
        fr = f"%D:%H:%M:%S"
    return time.strftime(fr, x)


def format_dt_(timestamp: int | datetime, style=None):
    if isinstance(timestamp, int):
        timestamp = datetime.fromtimestamp(timestamp, UTC)
    return format_dt(timestamp, style=style)
