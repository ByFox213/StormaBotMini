# -*- coding: utf-8 -*-
import logging
from os import environ, listdir

from nextcord.ext.commands import Bot

__all__ = (
    "get_token",
    "start_bot"
)


def get_token() -> str:
    token = environ.get('DISCORD_TOKEN', None)
    if token is not None:
        return token
    raise ValueError("Значени Token является None\nexport DISCORD_TOKEN=\"__TOKEN__\"")


def start_bot(owner_ids: list[int]) -> tuple[Bot, str]:
    logging.basicConfig(level=logging.INFO, filename=f"discordbot.log",
                        format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', encoding='utf-8', filemode="w")
    tk = get_token()
    bot = Bot(owner_ids=owner_ids)
    bot.remove_command('help')
    for file in listdir('./cogs'):
        if not file.endswith('.py'):
            continue
        fl = file[:-3]
        try:
            exec(f"from cogs.{fl} import {fl}")
            exec(f"bot.add_cog({fl}())")
        except ImportError as ex:
            print(f"Error load {fl}.py")
            logging.exception(ex, exc_info=True, stack_info=True)
    return bot, tk
