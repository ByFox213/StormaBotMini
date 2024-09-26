#!/usr/bin/env python3

import io
import logging
import os.path
from typing import TypeVar, Any, Iterable, Optional

import yaml
import orjson
from nextcord import Interaction, Embed, File, AllowedMentions, MessageFlags, Color, Permissions, Message, Member, \
    PartialInteractionMessage
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
    "text_to_file"
)

DataClassT = TypeVar("DataClassT", bound="BaseModel")
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
        if self.user is not None:
            _log.info(f"%s | %s(%s): %s", name, self.user.name, self.user.id, func_name)

    def get_langs(self) -> Lang:
        cl = self.client.lang
        data = cl.get(self.locale, None)
        if data is None:
            data = cl["en"]
        return data

    async def send(self,
                   content: Optional[str] = None,
                   send_file: bool = False,
                   *,
                   description: str = MISSING,
                   format_: Iterable = MISSING,
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
                   suppress_embeds: bool | None = None) -> PartialInteractionMessage | Message | None:
        if self.is_expired():
            return
        if not isinstance(content, Types):
            if (content is not None and len(content) > 2000) or send_file:
                return await super().send(file=text_to_file(content))
            return await super().send(content, embed=embed, embeds=embeds, file=file,
                                      files=files, view=view, tts=tts, delete_after=delete_after,
                                      allowed_mentions=allowed_mentions, flags=flags,
                                      ephemeral=ephemeral, suppress_embeds=suppress_embeds)
        locale = self.get_langs().other
        title: str = getattr(locale, content)
        if format_ is not MISSING:
            title = title.format(*(str(i) for i in format_))
        embed = Embed(title=title, description=description, color=Color.red())
        embed.set_footer(text=locale.find_bugs)
        return await super().send(embed=embed, ephemeral=True)


def split_list(iterable: list) -> tuple[list, list]:
    half = len(iterable) // 2
    return iterable[:half], iterable[half:]


def loads_yaml(filename: str,
               dc: DataClassT,
               example_date: str = None,
               rt: Any = None) -> DataClassT | Any:
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as file:
            if example_date is not None:
                file.write(example_date)
                return example_date
    with open(filename, "r", encoding="utf-8") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    if data is None:
        return rt
    return dc(**data)


def loads_json(filename: str,
               dc: DataClassT,
               example_date: Optional[str] = None,
               rt: Any = None) -> DataClassT | Any:
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
