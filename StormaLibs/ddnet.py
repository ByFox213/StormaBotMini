import io
from io import BytesIO

import nextcord
from PIL import Image, ImageDraw
from ddapi import DDPlayer, Query
from nextcord import SlashOption, Locale, Interaction, Embed, Color, File

from .misc import get_language

__all__ = (
    "humanize_pps",
    "nickname",
    "nickname_nr",
    "generate_profile_image",
    "server_get_status_ddos",
    "plural",
    "send_query",
    "text_to_file"
)

BASE_URL = 'https://ddnet.org'


def save(img) -> BytesIO:
    buf = BytesIO()
    img.save(buf, format='png')
    buf.seek(0)
    return buf


def center(size: int, area_size: int | float = 0) -> int:
    return int((area_size - size) / 2)


def round_rectangle(size: tuple[int, int], radius: int, *, color: tuple[int, ...]) -> Image.Image:
    width, height = size

    radius = min(width, height, radius * 2)
    width *= 2
    height *= 2

    corner = Image.new('RGBA', (radius, radius))
    draw = ImageDraw.Draw(corner)
    xy = (0, 0, radius * 2, radius * 2)
    draw.pieslice(xy, 180, 270, fill=color)

    rect = Image.new('RGBA', (width, height), color=color)
    rect.paste(corner, (0, 0))  # upper left
    rect.paste(corner.rotate(90), (0, height - radius))  # lower left
    rect.paste(corner.rotate(180), (width - radius, height - radius))  # lower right
    rect.paste(corner.rotate(270), (width - radius, 0))  # upper right

    return rect.resize(size, resample=Image.LANCZOS, reducing_gap=1.0)  # antialiasing


def plural(value: int, singular: str) -> str | bool:
    try:
        return singular if abs(value) == 1 else singular + 's'
    except TypeError:
        return False


def humanize_pps(pps: int) -> str:  # network
    if pps is None or pps < 0:
        return ''

    for unit in ('', 'k', 'm', 'g'):
        if pps < 1000:
            return str(pps) + unit

        pps = round(pps / 1000, 2)


nickname = SlashOption(name="nickname", name_localizations={Locale.ru: "никнейм"},
                       description="Player name",
                       description_localizations={Locale.ru: "Имя игрока"},
                       max_length=15)


def nickname_nr(number) -> SlashOption:
    return SlashOption(name=f"nickname{number}", name_localizations={Locale.ru: f"никнейм{number}"},
                       description="Player name",
                       description_localizations={Locale.ru: "Имя игрока"},
                       max_length=15, required=False)


async def generate_profile_image(self, data: DDPlayer, im):
    points = data.points
    point = 0
    if points is not None:
        point = points.points
    img, color = next(e for t, e in self.thresholds.items() if point >= t)
    base = self.profile_backgrounds.get(img).copy()

    canv = ImageDraw.Draw(base)

    width, height = base.size
    outer = 32
    inner = int(outer / 2)
    margin = outer + inner

    # draw bg
    size = (width - outer * 2, height - outer * 2)
    bg = round_rectangle(size, 12, color=(0, 0, 0, 150))
    base.alpha_composite(bg, dest=(outer, outer))

    # draw name
    lang = await get_language(data.last_finishes)
    flag = self.flags.get(lang)

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
    text = "UNRANKED"
    if points.rank is not None:
        text = f'#{points.rank}'

    _, _, w, h = self.font_big.getbbox(text)
    xy = (margin + center(w, points_width), y)
    canv.text(xy, text, fill='white', font=self.font_big)

    offset = h * 0.25  # true drawn height is only 3 / 4
    text = "None"
    if point is not None:
        text = str(point)

    _, _, w, h = self.font_bold.getbbox(text)
    suffix = plural(point, ' point').upper()
    _, _, w2, h2 = self.font_normal.getbbox(suffix)

    x = margin + center(w + w2, points_width)
    y = height - margin - offset

    canv.text((x, y - h), text, fill=color, font=self.font_bold)
    canv.text((x + w, y - h2), suffix, fill=color, font=self.font_normal)
    team = data.team_rank
    rank = data.rank

    # draw ranks
    types = {
        'TEAM RANK ': (team.rank, team.points),
        'RANK ': (rank.rank, rank.points)
    }

    _, _, _, h = self.font_bold.getbbox('A')
    yy = (margin + name_height + inner + h * 1.25, height - margin - h * 0.5)
    for (type_, (rank, pp)), y in zip(types.items(), yy):
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
        for text, color_, font in line[::-1]:
            _, _, w, h = font.getbbox(text)
            x -= w  # adjust x before drawing since we're drawing reverse
            if text == '   ':
                xy = ((x + w / 2, y - h * 0.75), (x + w / 2, y - 1))  # fix line width overflow
                canv.line(xy, fill=color_, width=1)
            else:
                canv.text((x, y - h), text, fill=color_, font=font)

    file = nextcord.File(save(base.convert('RGB')), filename=f'profile_{data.player}.png')
    return await im.send(file=file)


def server_get_status_ddos(server, pps_threshold, pps_ratio_min, pps_ratio_threshold) -> str:
    if not server.online4:
        return 'down'
    elif server.packets_rx > pps_threshold or server.packets_rx > pps_ratio_min and server.packets_rx / server.packets_tx > pps_ratio_threshold:
        return 'ddos'  # not necessarily correct but easy to understand
    return 'up'


async def send_query(player, msg, data: Query | None):
    if data is None or not data.data:
        embed = Embed(title=f"\"{player}\" не обнаружен", color=Color.red())
    else:
        embed = Embed(title=f"Возможно, вы имели в виду:\nникнейм, поинты\n\n", description="\n".join([f"``{i.name}``: {i.points}" for i in data.data]), color=Color.blue())
    if not isinstance(msg, Interaction):
        return await msg.send(embed=embed)
    return await msg.edit(embed=embed)


def text_to_file(text: str, filename: str = "text.txt", **kwargs) -> File:
    return File(io.StringIO(text), filename=filename, **kwargs)
