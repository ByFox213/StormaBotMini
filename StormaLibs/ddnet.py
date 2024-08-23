import urllib.parse
from os import listdir
from typing import Any, Generator, Iterable

import nextcord
from PIL import Image, ImageDraw
from nextcord import SlashOption, Locale
from ddapi import DDPlayer, DDStatus, Master

from .data.types import T, Nickname
from .grafic import round_rectangle, center, save
from .data.dataclass import DDnetConfig
from .times import seconds_to_hour
from .misc import get_language

__all__ = (
    "humanize_points",
    "humanize_pps",
    "nickname",
    "nickname_nr",
    "generate_profile_image",
    "checker",
    "get_url",
    "server_get_status_ddos",
    "plural",
    "country_size",
    "max_length_check",
    "most_played_sort",
    "most_played_generator",
    "get_files_image",
    "slugify2"
)

BASE_URL = 'https://ddnet.org'
slugify2_symbols = '[\t !"#$%&\'()*-/<=>?@[\\]^_`{|},.:]+'


def slugify2(_nickname: Nickname):
    """Needed for a link generator."""
    string = ""
    for symbol in _nickname:
        string += "-%s-" % ord(symbol) if symbol in slugify2_symbols or ord(symbol) >= 128 else symbol
    return string


def plural(value: int, singular: str) -> str:
    """Determines whether to put an "s" at the end of the."""
    try:
        return singular if abs(value) == 1 else singular + 's'
    except TypeError:
        return singular


def humanize_pps(pps: int) -> str:  # network
    """Turns numbers into more human-understandable values.

    humanize_pps(1049) = '1.05k'
    humanize_pps(1050) = '1.05k'
    humanize_pps(30245) = '30.25k'
    humanize_pps(1002000) = '1.0m'
    """
    if pps is None or pps < 0:
        return ''

    for unit in ('', 'k', 'm', 'g'):
        if pps < 1000:
            return str(pps) + unit
        pps = round(pps / 1000, 2)


def humanize_points(points: int) -> str:
    """Thousands turns into a more humanly comprehensible meaning.

    humanize_points(1049) = '1K'
    humanize_points(1050) = '1.1K'
    humanize_points(30245) = '30.2K'
    """
    if points < 1000:
        return str(points)
    points = round(points / 1000, 1)
    if points % 1 == 0:
        points = int(points)
    return f'{points}K'


nickname = SlashOption(name="nickname", name_localizations={Locale.ru: "никнейм"},
                       description="Player name",
                       description_localizations={Locale.ru: "Имя игрока"},
                       max_length=15)


def nickname_nr(number) -> SlashOption:
    """Necessary for deletion, repeating code."""
    return SlashOption(name=f"nickname{number}", name_localizations={Locale.ru: f"никнейм{number}"},
                       description="Player name",
                       description_localizations={Locale.ru: "Имя игрока"},
                       max_length=15, required=False)


def get_url(pl: str) -> str:
    """creating a user url to output to the user."""
    return f"https://ddnet.org/players/{slugify2(Nickname(urllib.parse.quote(pl)))}"


async def checker(ms: Master, clan: str, nicknames: list[Nickname]) -> list:
    """Receives nicknames of users from the clan"""
    cll = []
    nicknames = [i.lower() for i in nicknames]
    for i in ms.servers:
        q = [client.name for client in i.info.clients if
             client.name is not None and client.name.lower() in nicknames or client.clan == clan]
        if q:
            cll.append([f"{i.info.name}: {i.info.map.get('name', '')}", q])
    return cll


async def generate_profile_image(self, data: DDPlayer, im):
    point, outer = 0, 32
    rank_str, points_str = "UNRANKED", "None"
    ranks_types = {
        'TEAM RANK ': (data.team.rank, data.team.points),
        'RANK ': (data.rank.rank, data.rank.points)
    }
    points = data.points
    if points is not None:
        point = points.points

    img, color = next(e for t, e in self.thresholds.items() if point >= t)

    base = self.profile_backgrounds.get(img).copy()
    canv = ImageDraw.Draw(base)
    width, height = base.size

    inner = int(outer / 2)
    margin = outer + inner

    # draw bg
    size = (width - outer * 2, height - outer * 2)
    bg = round_rectangle(size, 12, color=(0, 0, 0, 150))
    base.alpha_composite(bg, dest=(outer, outer))

    # draw name
    lang = await get_language(data.last_finishes)
    flag = self.flags.get(lang)
    if flag is None:
        flag = self.flags.get("UNK")
    flag_w, flag_h = flag.size

    name = ' ' + data.player
    _, _, w, _ = self.font_bold.getbbox(name)
    _, _, _, h = self.font_bold.getbbox('yA')  # hardcoded to align names
    name_height = 50
    radius = int(name_height / 2)

    size = (flag_w + w + radius * 2, name_height)
    name_bg = round_rectangle(size, radius, color=(150, 150, 150, 75))
    base.alpha_composite(name_bg, dest=(margin, margin))
    x = margin + radius
    dest = (x, margin + center(flag_h, name_height))
    base.alpha_composite(flag, dest=dest)

    xy = (x + flag_w, margin + center(h, name_height))
    canv.text(xy, name, fill='white', font=self.font_bold)

    # draw points
    points_width: float = (width - margin * 2) / 3
    x = margin + points_width + inner
    y = margin + name_height + inner
    xy = ((x, y), (x, height - margin))
    canv.line(xy, fill='white', width=3)
    if points.rank is not None:
        rank_str = f'#{points.rank}'

    _, _, w, h = self.font_big.getbbox(rank_str)
    xy = (margin + center(w, points_width), y)
    canv.text(xy, rank_str, fill='white', font=self.font_big)

    offset = h * 0.25  # true drawn height is only 3 / 4
    if point is not None:
        points_str = str(point)

    _, _, w, h = self.font_bold.getbbox(points_str)
    suffix = plural(point, ' point').upper()
    _, _, w2, h2 = self.font_normal.getbbox(suffix)

    x = margin + center(w + w2, points_width)
    y = height - margin - offset

    canv.text((x, y - h), points_str, fill=color, font=self.font_bold)
    canv.text((x + w, y - h2), suffix, fill=color, font=self.font_normal)

    # draw ranks
    _, _, _, h = self.font_bold.getbbox('A')
    yy = (margin + name_height + inner + h * 1.25, height - margin - h * 0.5)
    for (type_, (rank, pp)), y in zip(ranks_types.items(), yy):
        line = [(type_, 'white', self.font_normal)]
        if rank is None:
            line.append(('UNRANKED', (150, 150, 150), self.font_bold))
        else:
            line.extend((
                (f'#{rank}', 'white', self.font_bold),
                ('   ', 'white', self.font_bold),  # border placeholder
                (str(pp), color, self.font_bold),
                (plural(pp, ' point').upper(), color, self.font_normal),
            ))

        x = width - margin
        for points_str, color_, font in line[::-1]:
            _, _, w, h = font.getbbox(points_str)
            x -= w  # adjust x before drawing since we're drawing reverse
            if points_str == '   ':
                xy = ((x + w / 2, y - h * 0.75), (x + w / 2, y - 1))  # fix line width overflow
                canv.line(xy, fill=color_, width=1)
            else:
                canv.text((x, y - h), points_str, fill=color_, font=font)

    file = nextcord.File(save(base.convert('RGB')), filename=f'profile_{data.player}.png')
    return await im.send(file=file)


def server_get_status_ddos(server: DDStatus, ddnet_config: DDnetConfig) -> str:
    """Receive server state as a text form."""
    if not server.online4:
        return 'down'
    elif (server.packets_rx > ddnet_config.PPS_THRESHOLD or
          server.packets_rx > ddnet_config.PPS_RATIO_MIN and
          server.packets_rx / server.packets_tx > ddnet_config.PPS_RATIO_THRESHOLD):
        return 'ddos'
    return 'up'


def get_files_image(_dir: str, type_file: str = None) -> dict[str, Image]:
    """Getting image files from a folder to the dictionary."""
    data = {}
    if type_file is None:
        type_file: str = "png"

    remv = len(type_file)
    for filename in listdir(f"{_dir}"):
        if filename.endswith(type_file):
            fl = Image.open(f'{_dir}/{filename}')
            if fl.mode != "RGBA":
                fl = fl.convert(mode="RGBA")
            data[filename[:len(filename) - remv - 1]] = fl
    return data


def country_size(name: str, key: int, org: int = 3) -> str:
    """Reduces the name to "org".

    country_size('GERMANY') = 'GER'
    country_size('RUSSIA2') = 'RUS2'
    """
    num = ''
    if len(name) > key and name[key].isnumeric():
        num = name[key]
    return name[:org] + num


def max_length_check(numbers: Iterable[T]) -> int:
    """Need for determining the length of spaces and readability in the playtime command."""
    if not numbers:
        return 20
    number = max(numbers)
    return number + 2 if number > 18 else 20


def most_played_sort(x: list, func=lambda v: (v.key, v.seconds_played)) -> list[tuple[Any, Any]]:
    """Collects the data into a generator and sorts it."""
    return sorted((func(i) for i in x), key=lambda h: h[1], reverse=True)


def most_played_generator(max_length: int, sort: list) -> Generator[str, Any, None]:
    """Creates a generator for later use"""
    return (f"{i:<{max_length}}{seconds_to_hour(o)}" for i, o in sort)
