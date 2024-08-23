import io

import plotly.graph_objs as go
from PIL import ImageDraw, Image
from nextcord import File


def create_image(x: list,
                 y: list,
                 name: any,
                 title: str,
                 yaxis: str,
                 xaxis: str,
                 trace_name: list = None,
                 legend_h: bool = True,
                 mode: str = None) -> File:
    if mode is None:
        mode = 'lines'
    fig = go.Figure(layout=go.Layout(
        title=title,
        yaxis=dict(title=yaxis),
        xaxis=dict(title=xaxis),
        template="plotly_dark"
    ))
    if trace_name is None:
        trace_name = ["." for _ in range(len(x))]
    for _x, _y, _name in zip(x, y, trace_name):
        fig.add_trace(go.Scatter(x=_x, y=_y, mode=mode, name=_name))
    if legend_h:
        fig.update_layout(legend_orientation="h")
    cimage = io.BytesIO()
    fig.write_image(cimage, 'png', 4, 2, validate=True)
    del fig
    cimage.seek(0)
    return File(cimage, filename=str(name)+'.png')


def save(img) -> io.BytesIO:
    buf = io.BytesIO()
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

