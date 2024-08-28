#!/usr/bin/env python3

import io
import logging
import os.path
from datetime import datetime
from typing import TypeVar, Any, Iterable
import yaml
import orjson
from nextcord import Interaction, Embed, File, AllowedMentions, MessageFlags, Color, Permissions, Message
from nextcord.utils import MISSING
from nextcord.ui import View

from .data.dataclass import Lang
from .data.enums import Types

__all__ = (
    "check_count_songs",
    "StormBotInter",
    "split_list",
    "loads_yaml",
    "loads_json",
    "text_to_file",
    "edit_logging_file",
    "send_query"
)

DateClassT = TypeVar("DateClassT", bound="dateclass")
_log = logging.getLogger(__name__)


def check_count_songs(songs_count_limit,
                      songs_count: int,
                      new_songs_count: int) -> bool:
    count = songs_count + new_songs_count
    if count > songs_count_limit:
        return True
    return False


class StormBotInter(Interaction):
    def __init__(self, *, data, state):
        super().__init__(data=data, state=state)
        self.bot_name = self.client.bot_name

    def func(self, func_name: str, name: str = ''):
        if name != '':
            name = f'{name} | '
        _log.info(f"%s | %s(%s): %s", name, self.user.name, self.user.id, func_name)

    def get_langs(self) -> Lang:
        cl = self.client.lang
        data = cl.get(self.locale, None)
        if data is None:
            data = cl["en"]
        return data

    async def _send(self,
                    content: str | None = None,
                    *,
                    embed: Embed = MISSING,
                    embeds: list[Embed] = MISSING,
                    file: File = MISSING,
                    files: list[File] = MISSING,
                    view: View = MISSING,
                    tts: bool = False,
                    delete_after: float | None = None,
                    allowed_mentions: AllowedMentions = MISSING,
                    flags: MessageFlags | None = None,
                    ephemeral: bool | None = None,
                    suppress_embeds: bool | None = None) -> Message | None:
        if not self.response.is_done():
            return await self.response.send_message(
                content=content,
                embed=embed,
                embeds=embeds,
                file=file,
                files=files,
                view=view,
                tts=tts,
                ephemeral=ephemeral,
                delete_after=delete_after,
                allowed_mentions=allowed_mentions,
                flags=flags,
                suppress_embeds=suppress_embeds,
            )
        return await self.followup.send(
            content=content,  # type: ignore
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            view=view,
            tts=tts,
            ephemeral=ephemeral,
            delete_after=delete_after,
            allowed_mentions=allowed_mentions,
            flags=flags,
            suppress_embeds=suppress_embeds,
        )

    async def send(self,
                   content: str | None = None,
                   send_file: bool = False,
                   *,
                   description: str = MISSING,
                   format_: Iterable = None,
                   embed: Embed = MISSING,
                   embeds: list[Embed] = MISSING,
                   file: File = MISSING,
                   files: list[File] = MISSING,
                   view: View = MISSING,
                   tts: bool = False,
                   delete_after: float | None = None,
                   allowed_mentions: AllowedMentions = MISSING,
                   flags: MessageFlags | None = None,
                   ephemeral: bool | None = None,
                   suppress_embeds: bool | None = None) -> Message | None:
        if self.is_expired():
            return
        if not isinstance(content, Types):
            if (content is not None and len(content) > 2000) or send_file:
                return await self._send(file=text_to_file(content))
            return await self._send(content, embed=embed, embeds=embeds, file=file,
                                    files=files, view=view, tts=tts, delete_after=delete_after,
                                    allowed_mentions=allowed_mentions, flags=flags,
                                    ephemeral=ephemeral, suppress_embeds=suppress_embeds)
        locale = self.get_langs().ddnet
        title: str = getattr(locale, content)
        if format_ is not None:
            title = title.format(*(str(i) for i in format_))
        embed = Embed(title=title, description=description, color=Color.red())
        return await self._send(embed=embed, ephemeral=True)


def split_list(iterable: list) -> tuple[list, list]:
    half = len(iterable) // 2
    return iterable[:half], iterable[half:]


def loads_yaml(filename: str,
               dc: DateClassT,
               example_date: str = None,
               rt: Any = None) -> DateClassT | Any:
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as file:
            if example_date is not None:
                file.write(example_date)
    with open(filename, "r", encoding="utf-8") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    if data is None:
        return rt
    return dc(**data)


def loads_json(filename: str,
               dc: DateClassT,
               example_date: str = None,
               rt: Any = None) -> DateClassT | Any:
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as file:
            if example_date is not None:
                file.write(example_date)
    with open(filename, "r", encoding="utf-8") as file:
        data = orjson.loads(file.read())
    if data is None:
        return rt
    return dc(**data)


def text_to_file(text: str, filename: str = "text.txt", **kwargs) -> File:
    return File(io.StringIO(text), filename=filename, **kwargs)


def edit_logging_file(logger, dt: datetime):
    log = logging.getLogger()
    for hdlr in log.handlers[:]:
        if isinstance(hdlr, logging.FileHandler):
            log.removeHandler(hdlr)
    date = dt.strftime("%Y.%m.%d")
    log.addHandler(logging.FileHandler(f"{logger.dir}/{date}.log", 'a'))


async def send_query(im: StormBotInter):
    return await im.send(embed=Embed(title="The user was not detected", color=Color.red()))
