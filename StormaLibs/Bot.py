from typing import Any

from ddapi import Query
from nextcord import Interaction, Embed, Color
from nextcord.ext import commands

from .StormaLib import StormBotInter
from .data.dataclass import Config, LangDDnet

__all__ = (
    "Bot",
    "send_query"
)


class Bot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # settings

        self.dat: Config = kwargs.pop("config")
        self.lang: Config = kwargs.pop("lang")
        self.bot_name: str = kwargs.pop("bot_name", "StormaBot")

        self.servers: dict = {}

        super().__init__(*args, **kwargs)

    def get_interaction(self, data, *, cls=Interaction):
        return super().get_interaction(data, cls=StormBotInter)


async def send_query(player: str, msg: StormBotInter, local: LangDDnet, data: Query | None):
    if data is None or not data.data:
        embed = Embed(title=local.plr_not_player.format(player), color=Color.red())
    else:
        embed = Embed(title=f"{local.perhaps_you}:\nname, points\n\n",
                      description="\n".join([f"``{i.name}``: {i.points}" for i in data.data]), color=Color.blue())
    return await msg.send(embed=embed)
