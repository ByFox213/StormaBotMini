import time

__all__ = (
    "seconds_to_hour",
    "seconds_to_time"
)


def seconds_to_hour(seconds: int) -> float:
    if seconds < 360:  # seconds < hour / 10
        return 0.0
    data = str(seconds / 3600)
    return float(data[:data.rfind(".")+2])


def seconds_to_time(seconds: int | float) -> str:
    x = time.gmtime(seconds)
    if x.tm_mday > 1:
        return time.strftime(f"%D:%H:%M:%S", x)
    return time.strftime("%H:%M:%S", x)
