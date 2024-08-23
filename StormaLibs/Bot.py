from typing import Any

from nextcord import Interaction
from nextcord.ext import commands

from .StormaLib import StormBotInter
from .data.dataclass import Config

__all__ = (
    "Bot",
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