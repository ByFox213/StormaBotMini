from typing import Optional

from ddapi import MostPlayed, MostPlayedMaps
from pydantic import BaseModel, Field


class CommmandLg(BaseModel):
    name: str = Field(default=None)
    desc: str = Field(default=None)
    name_lang: dict = Field(default=None)
    desc_lang: dict = Field(default=None)
    dm: bool = Field(default=False)


class CommandsLang(BaseModel):
    rank_points: CommmandLg
    settings: CommmandLg
    ddos: CommmandLg
    player_top_10: CommmandLg
    tee: CommmandLg
    add_tee: CommmandLg
    remove_tee: CommmandLg
    ddnet_map: CommmandLg
    join_history: CommmandLg
    leaders: CommmandLg
    rank: CommmandLg
    profile: CommmandLg
    playtime: CommmandLg
    find: CommmandLg
    player: CommmandLg
    map_claimed: CommmandLg
    clans: CommmandLg
    clan: CommmandLg
    points: CommmandLg
    dnd_roll: CommmandLg
    dnd_stats: CommmandLg


class LoggerConfig(BaseModel):
    level: str = Field(default="INFO")
    dir: str = Field(default="logs")


class DDnetConfig(BaseModel):
    flag: str
    font: str
    profile_backgrounds: str
    PPS_THRESHOLD: int
    PPS_RATIO_MIN: int
    PPS_RATIO_THRESHOLD: float
    thresholds: dict


class ConfConfigs(BaseModel):
    cogs_dir: str
    logger: LoggerConfig
    ddnet: DDnetConfig


class Config(BaseModel):
    configs: ConfConfigs
    token: str = Field(default=None)


class Find(BaseModel):
    server: str
    fsw: str


class LangDDnet(BaseModel):
    points_graph: str
    powered_by: str
    pnf: str
    points: str
    first_finish: str
    last_finish: str
    date: str
    time: str
    country: str
    favorite_partners: str
    finishes: str
    name: str
    hours: str
    cnftp: str
    ttf: str
    CAMC10P: str
    Youhavenorights: str
    NFSP: str
    clan: str
    clans: str
    tuo: str
    find: Find
    sopfp: str
    playtime: str
    mph: str
    cph: str
    gph: str
    tph: str
    nomt: str
    date_history: str
    cset: str
    plr_not_player: str
    perhaps_you: str
    mapper: str
    map_not_found: str
    finishes_tee: str
    med_time: str
    joined: str
    ranks: str
    t_ranks: str
    max_finishes: str
    biggest_team: str
    noop: str
    err_component: str
    is_bot: str
    not_perm: str
    not_perm_user: str
    RE: str
    idtgag: str
    not_owner: str
    not_activity: str
    dm_not_guild: str


class Lang(BaseModel):
    ddnet: LangDDnet


class Playtime(BaseModel):
    most_played_maps: Optional[list[MostPlayedMaps]] = None
    most_played_gametypes: Optional[list[MostPlayed]] = None
    most_played_categories: Optional[list[MostPlayed]] = None

