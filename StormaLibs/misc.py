from collections import Counter
from os import listdir

from PIL import Image
from ddapi import LastFinish


def firth(iterable) -> any:
    for i in iterable:
        return i


def get_files(dir_files: str, type_file: str = None) -> dict[str, Image]:
    data = {}
    if type_file is None:
        type_file: str = "png"
    remv = len(type_file)
    for filename in listdir(f"{dir_files}"):
        if filename.endswith(type_file):
            fl = Image.open(f'{dir_files}/{filename}')
            if fl.mode != "RGBA":
                fl = fl.convert(mode="RGBA")
            data[filename[:len(filename) - remv - 1]] = fl
    return data


async def get_language(lf: list[LastFinish]) -> str:
    if lf is None:
        return "UNK"
    return firth(Counter(i.country for i in lf))
