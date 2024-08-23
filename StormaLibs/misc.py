from collections import Counter
from typing import Iterable, Any

from ddapi import LastFinish


def firth(iterable: Iterable) -> Any:
    for i in iterable:
        return i


async def get_language(lf: list[LastFinish]) -> str:
    if lf is None:
        return "UNK"
    return firth(Counter(i.country for i in lf))

