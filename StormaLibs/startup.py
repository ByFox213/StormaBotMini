# -*- coding: utf-8 -*-
import logging
import os
from typing import Callable
from datetime import datetime
from os import environ, listdir, path, mkdir

import yaml
from nextcord.utils import utcnow

from .StormaLib import loads_yaml
from .Bot import Bot
from .data.dataclass import Config, Lang, LoggerConfig

__all__ = (
    "get_token",
    "create_logger",
    "start_bot"
)


def get_files(
        _dir: str,
        type_file: str = None,
        func: Callable = lambda _: False,
        func_out: Callable = lambda f: f.read()
) -> dict[str, any]:
    """Getting image files from a folder to the dictionary."""
    files = {}
    if type_file is None:
        type_file: str = "png"

    cwd = os.getcwd()
    remv = len(type_file)
    for filename in listdir(cwd+'/'+_dir):
        if func(filename) or not filename.endswith(type_file):
            continue
        with open(cwd+'/'+_dir+'/'+filename, "r", encoding="utf-8") as f:
            files[filename[:len(filename) - remv - 1]] = func_out(f)
    return files


def get_py_files_from_folder(cogs_dir: str) -> list:
    rt = []
    for filename in listdir(cogs_dir):
        if filename.endswith('.py'):
            rt.append(filename[:-3])
    return rt


def get_token(ym: Config) -> str:
    token = environ.get('DISCORD_TOKEN', None)
    if token is not None:
        return token
    token_yaml = ym.token
    if token_yaml != "None":
        return token_yaml
    raise ValueError("DISCORD_TOKEN IS NONE")


def load_cog(bot: Bot, config: Config) -> None:  # ignore: W0613
    for file in get_py_files_from_folder(config.configs.cogs_dir):
        try:
            exec(f"from cogs.{file} import {file}")
            exec(f"bot.add_cog({file}(bot=bot, config=config))")
        except ImportError as ex:
            print(f"Error load {file}.py")
            logging.exception(ex, exc_info=True, stack_info=True)


def create_logger(logger: LoggerConfig, dt: datetime) -> None:
    lg = logger.level.upper()
    lvl = logging.INFO
    if lg in ["DEBUG", "INFO", "WARN", "ERROR", "critical"]:
        lvl = getattr(logging, lg)

    if not path.isdir(logger.dir):
        mkdir(logger.dir)
    date = dt.strftime("%Y.%m.%d")

    logging.basicConfig(
        level=lvl,
        filename=f"{logger.dir}/{date}.log",
        format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
        encoding='utf-8',
        filemode="w"
    )


def start_bot(owner_ids: list[int]) -> tuple[Bot, str]:
    timestamp = utcnow()
    config = loads_yaml('config.yaml', Config)

    lang = get_files(
        "language",
        'yaml',
        lambda x: x == "commands.yaml",
        lambda x: Lang(**yaml.load(x, Loader=yaml.FullLoader))
    )

    # Bot and load Cog

    create_logger(config.configs.logger, timestamp)

    bot = Bot(
        owner_ids=owner_ids,
        lang=lang,
        config=config
    )
    bot.remove_command('help')
    load_cog(bot, config)
    return bot, get_token(config)
