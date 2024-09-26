import logging
from ast import literal_eval
from os import getcwd

import nextcord
from PIL import ImageFont
from ddapi import DDPlayer, Master
from nextcord import SlashOption, Embed, Color, Locale
from nextcord.ext import commands
from nextcord.utils import utcnow
from ddapi import DDnetApi, DDstats

from StormaLibs import clang, StormBotInter, send_query, Types, nickname, nickname_nr
from StormaLibs.data.dataclass import LangDDnet, Config
from StormaLibs.times import seconds_to_time
from StormaLibs.grafic import create_image
from StormaLibs.country import FLAG_UNK, flag
from StormaLibs.ddnet import country_size, humanize_pps, generate_profile_image, \
    server_get_status_ddos, get_files_image, create_embed_playtime


class DDnet(commands.Cog):
    def __init__(self, config: Config, **_):
        self.configs = config.configs
        cwd = getcwd()
        configs = config.configs
        font = cwd + configs.ddnet.font

        # API

        self.dd = DDnetApi()
        self.ddrace = DDstats()

        # settings
        self.skins_temp: dict[str, str] = {}
        self.thresholds = {k: literal_eval(p) for k, p in configs.ddnet.thresholds.items()}

        # load_data
        self.font_normal = ImageFont.truetype(f'{font}/normal.ttf', 24)
        self.font_bold = ImageFont.truetype(f'{font}/bold.ttf', 34)
        self.font_big = ImageFont.truetype(f'{font}/bold.ttf', 48)
        self.flags = get_files_image(f"{cwd}{configs.ddnet.flag}")
        self.profile_backgrounds = get_files_image(f"{cwd}{configs.ddnet.profile_backgrounds}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"| The bot has started working")

    @nextcord.slash_command(name="ddnet")
    async def ddnet(self, im: StormBotInter):
        pass

    @ddnet.subcommand(name=clang.profile.name,
                      description=clang.profile.desc,
                      name_localizations=clang.profile.name_lang,
                      description_localizations=clang.profile.desc_lang)
    async def profile(self, im: StormBotInter, player: str = nickname):
        im.func("ddnet_profile", player)
        local = im.get_langs().ddnet
        await im.response.defer()

        data: DDPlayer = await self.dd.player(player)
        if data is None:
            return await send_query(player, im, local, await self.dd.query(player))
        await im.client.loop.create_task(generate_profile_image(self, data, im))

    @ddnet.subcommand(name=clang.playtime.name,
                      description=clang.playtime.desc,
                      name_localizations=clang.playtime.name_lang,
                      description_localizations=clang.playtime.desc_lang)
    async def playtime(self, interaction: StormBotInter, player: str = nickname):
        """Отправляет сообщение с данными пользователя"""
        await interaction.response.defer()
        interaction.func("playtime", player)
        embed = await create_embed_playtime(interaction, self.ddrace, player)
        return await interaction.send(embed=embed)

    @ddnet.subcommand(name=clang.find.name,
                      description=clang.find.desc,
                      name_localizations=clang.find.name_lang,
                      description_localizations=clang.find.desc_lang)
    async def ddnet_find(self, im: StormBotInter, player: str = nickname):
        im.func("ddnet_find", player)
        local = im.get_langs().ddnet
        await im.response.defer()

        fi = local.find
        servers: Master = await self.dd.master()
        if servers is None:
            return await im.send(Types.RE)

        count: int = 1
        find_: dict = {}
        async for info in servers.get_info():
            for user in info.clients:
                if user.name != player:
                    continue

                server_name = str(info.name)
                if find_.get(server_name) is None:
                    find_[server_name] = []

                find_[server_name].append(f"- {count}. {info.map.get('name', '')}\n")
                count += 1

        find = ''.join([f"\n{k}:\n{''.join(i)}" for k, i in find_.items()])
        ln_find = len(find)

        if ln_find == 0:
            return await im.send(embed=Embed(title=local.pnf, color=im.user.color), ephemeral=True)

        if ln_find > 2000:
            return await im.send(
                f"{fi.fsw.format(count - 1, player)}\n"
                f"{find}\n\n{local.powered_by} {self.dd.powered()} | {local.NFSP}: {len(servers)}",
                True
            )
        embed: Embed = Embed(
            title=fi.fsw.format(count - 1, player),
            color=im.user.color,
            description=find
        )

        embed.set_footer(text=f"{local.powered_by} {self.dd.powered()} | {local.NFSP}: {len(servers)}")
        return await im.send(embed=embed)

    @ddnet.subcommand(name=clang.player.name,
                      description=clang.player.desc,
                      name_localizations=clang.player.name_lang,
                      description_localizations=clang.player.desc_lang)
    async def ddnet_player(self, im: StormBotInter, player: str = nickname):
        im.func("ddnet_player", player)
        local = im.get_langs().ddnet

        await im.response.defer()
        data: DDPlayer = await self.dd.player(player)

        if data is None:
            return await send_query(player, im, local, await self.dd.query(player))

        poi, ff = data.points, data.first_finish
        if ff is None or data.last_finishes is None:
            return await im.send(embed=Embed(title=local.pnf, color=im.user.color), ephemeral=True)

        lf, fp = data.last_finishes[0], data.favorite_partners
        embed: Embed = Embed(
            title=f"{poi.rank}. {data.player}",
            description=f"{local.points}: {poi.points}/{poi.total}",
            color=im.user.color)
        embed.add_field(
            name=local.first_finish,
            value=f"{ff.map} | {seconds_to_time(ff.time)}\n{local.date}: <t:{int(ff.timestamp)}>")
        embed.add_field(
            name=local.last_finish,
            value=f"{lf.map} | {seconds_to_time(lf.time)}\n"
                  f"{local.date}: <t:{int(lf.timestamp)}>",
            inline=False)

        if fp is not None and len(fp) >= 3:
            for i in [fp[0], fp[1], fp[2]]:
                embed.add_field(
                    name=local.favorite_partners,
                    value=f"{local.name}: {i.name}\n{local.finishes}: {i.finishes}"
                )

        embed.set_footer(text=f"{local.powered_by} {self.dd.powered()}")
        return await im.send(embed=embed)

    @ddnet.subcommand(name=clang.map_claimed.name,
                      description=clang.map_claimed.desc,
                      name_localizations=clang.map_claimed.name_lang,
                      description_localizations=clang.map_claimed.desc_lang)
    async def ddnet_map_claimed(self, im: StormBotInter, player: str = nickname,
                                limit: int = SlashOption(required=False, default=20, max_value=100)):
        im.func("ddnet_map_claimed", player)
        local = im.get_langs().ddnet
        await im.response.defer()

        usr = await self.dd.player(player)
        if usr is None or usr.types is None:
            return await send_query(player, im, local, await self.dd.query(player))

        maps = sorted((
                (map_name, data.get("finishes"))
                for typ, p in usr.types.model_dump().items()
                if p is not None
                for map_name, data in p.get('maps').items()
                if data is not None
            ), key=lambda x: x[1], reverse=True)[:limit]

        desk = "\n".join(f"``{map_name}``:  {count}" for map_name, count in maps)
        if len(desk) > 2000:
            desk = f"{local.nomt}\n\n" + desk.replace('`', '') + f"\n\n{local.powered_by} {self.dd.powered()}"
            return await im.send(desk, True)

        embed = Embed(title=local.nomt, description=desk, color=Color.purple())
        embed.set_footer(text=f"{player}{usr.emoji} | {local.powered_by} {self.dd.powered()}")
        return await im.send(embed=embed)

    @ddnet.subcommand(name=clang.clans.name,
                      description=clang.clans.desc,
                      name_localizations=clang.clans.name_lang,
                      description_localizations=clang.clans.desc_lang)
    async def ddnet_clans(self, im: StormBotInter,
                          count: int = SlashOption(
                              name="count",
                              min_value=10,
                              max_value=250,
                              default=None,
                              required=False
                          )):
        if count is None:
            count = 10
        im.func("ddnet_clans", str(count))
        local = im.get_langs().ddnet

        await im.response.defer()

        master: Master = await self.dd.master()
        if master is None:
            return await im.send(Types.RE)
        try:
            dat = master.get_clans(count)
        except TypeError:
            logging.exception("ddnet_clans exception TypeError: type_master: %s, master_data: %s",
                              (type(master), master))
            return await im.send(Types.RE)

        desk = local.tuo + "\n" + "\n".join(f"``{count}``, ``{n}``, {o}" for count, (n, o) in enumerate(dat, 1))
        if len(desk) > 2000:
            desk = (f"{local.clans}: {count}\n\n" + desk.replace('`',  '') +
                    f"\n\n{local.powered_by} {self.dd.powered()}")
            return await im.send(desk, True)

        embed = Embed(title=f"{local.clans}: {count}", description=desk, color=im.user.color)
        embed.set_footer(text=f"{local.powered_by} {self.dd.powered()}")
        return await im.send(embed=embed)

    @ddnet.subcommand(name=clang.clan.name,
                      description=clang.clan.desc,
                      name_localizations=clang.clan.name_lang,
                      description_localizations=clang.clan.desc_lang)
    async def ddnet_clan(self, im: StormBotInter, clan: str):
        im.func("ddnet_clan", clan)

        local = im.get_langs().ddnet
        await im.response.defer()

        master: Master = await self.dd.master()
        if master is None or not master:
            return await im.send(Types.RE)
        clients = [(info.name, client.name)
                   async for info in master.get_info()
                   for client in info.clients
                   if client.clan == clan and client.clan != ''
                   if client is not None and client.clan is not None]

        clients_str, e = '', ''
        for server_name, client_name in clients[:100]:
            if e != server_name:
                e = server_name
                clients_str += f'\n{server_name}:\n'
            clients_str += f'``{client_name}``\n'

        desk = f"{local.noop}: {len(clients)}\n\n{clients_str}"
        if len(desk) > 2000:
            return await im.send(f"{local.clan}: {clan}\n\n" + desk.replace('``', ''))
        return await im.send(
            embed=Embed(
                title=f"{local.clan}: {clan}", description=desk, color=im.user.color
            ).set_footer(text=f"{local.powered_by} {self.dd.powered()}"))

    @ddnet.subcommand(name=clang.points.name,
                      description=clang.points.desc,
                      name_localizations=clang.points.name_lang,
                      description_localizations=clang.points.desc_lang)
    async def points(self, im: StormBotInter,
                     _player: str = nickname,
                     player1: str = nickname_nr(1),
                     player2: str = nickname_nr(2),
                     player3: str = nickname_nr(3),
                     player4: str = nickname_nr(4),
                     player5: str = nickname_nr(5),
                     player6: str = nickname_nr(6),
                     player7: str = nickname_nr(7),
                     player8: str = nickname_nr(8),
                     player9: str = nickname_nr(9),
                     mode: str = SlashOption(required=False, description='default: lines', default='lines',
                                             choices=["lines+markers", "markers"])
                     ):
        ppl = list(
            set([
                i
                for i in [_player, player1, player2, player3, player4, player5, player6, player7, player8, player9]
                if i is not None
            ])
        )
        im.func("points", str(ppl))
        local = im.get_langs().ddnet
        await im.response.defer()

        times, points, players = [], [], []
        for player in ppl:
            players.append(player)
            times.append([])
            points.append([])

            usr = await self.ddrace.player(player)
            if usr is None:
                return await send_query(_player, im, local, await self.dd.query(_player))
            if usr.points_graph is None or len(usr.points_graph) < 5:
                return await im.send(Types.idtgag, description=f"nickname: {player}")
            for i in usr.points_graph:
                points[-1].append(i.points)
                times[-1].append(i.date)
        for i in points:
            i.append(i[-1])

        all_times = []
        for i in times:
            all_times.append(i[-1])

        max_time = max(all_times)
        for i in times:
            i.append(max_time)

        fl = create_image(
            times,
            points,
            f"{im.user.id}_points",
            f"{local.date_history}: {players}",
            local.points,
            local.date,
            players,
            False,
            mode
        )
        return await im.send(file=fl)

    @ddnet.subcommand(name=clang.rank_points.name,
                      description=clang.rank_points.desc,
                      name_localizations=clang.rank_points.name_lang,
                      description_localizations=clang.rank_points.desc_lang)
    async def rank_points(self, im: StormBotInter,
                          player: str = nickname,
                          mode: str = SlashOption(required=False, description='default: lines', default='lines',
                                                  choices=["lines+markers", "markers"])
                          ):
        im.func("rank_points", str(player))
        local = im.get_langs().ddnet
        usr = await self.ddstats_request(im, player, local)
        if usr is None:
            return

        if usr.points_graph is None or len(usr.points_graph) < 5:
            return await im.send(Types.idtgag)

        times, points = [], [[], []]
        for i in usr.points_graph:
            points[0].append(i.rank_points)
            points[1].append(i.team_points)
            times.append(i.date)

        fl = create_image(
            [times, times],
            points,
            f"{im.user.id}_rank_points",
            f"rank points: {player}",
            local.points,
            local.date,
            ["rank_points", "team_points"],
            True,
            mode
        )
        return await im.send(file=fl)

    @ddnet.subcommand(name=clang.ddnet_map.name,
                      description=clang.ddnet_map.desc,
                      name_localizations=clang.ddnet_map.name_lang,
                      description_localizations=clang.ddnet_map.desc_lang)
    async def ddnet_map(self, im: StormBotInter,
                        map_name: str = SlashOption(name="map", name_localizations={Locale.ru: "карта"})):
        im.func("points", map_name)
        local = im.get_langs().ddnet

        await im.response.defer()

        mapi = await self.dd.map(map_name)
        if mapi is None:
            return await im.send(embed=Embed(title=local.map_not_found.format(map=map_name), color=Color.red()))

        embed = Embed(title=f"{mapi.type} {mapi.name} | {'☆☆☆☆☆'.replace('☆', '★', mapi.difficulty)}",
                      description=f"{local.mapper}: ``{mapi.mapper}``\n"
                                  f"{local.finishes_tee.format(mapi.finishes, mapi.finishers)}\n"
                                  f"{local.biggest_team}: ``{mapi.biggest_team}``",
                      url=mapi.website, color=im.user.color)

        embed.set_thumbnail(url=mapi.thumbnail)
        embed.add_field(name=local.med_time, value=seconds_to_time(mapi.median_time), inline=False)
        for ranks, name in [
            [
                (
                        f"{flag(i.country)}{i.rank}. ``{' & '.join(i.players)}`` | {seconds_to_time(i.time)}"
                        for i in mapi.team_ranks[:10]
                ), local.t_ranks],
            [
                (
                        f"{flag(i.country)}{i.rank}. ``{i.player}`` | {seconds_to_time(i.time)}"
                        for i in mapi.ranks[:15]
                ), local.ranks],
            [
                (
                        f"{i.rank}. ``{i.player}``: {i.num}"
                        for i in mapi.max_finishes
                ), local.max_finishes]
        ]:
            if ranks:
                embed.add_field(name=name, value="\n".join(ranks))
        embed.set_footer(text=f"{local.powered_by} {self.dd.powered()}")
        return await im.send(embed=embed)

    @ddnet.subcommand(name=clang.player_top_10.name,
                      description=clang.player_top_10.desc,
                      name_localizations=clang.player_top_10.name_lang,
                      description_localizations=clang.player_top_10.desc_lang)
    async def top_1s(self, im: StormBotInter, player: str = nickname):
        im.func("player_top_10", player)
        local = im.get_langs().ddnet
        usr = await self.ddstats_request(im, player, local)
        if usr is None:
            return

        list_top1s = ["rank | team_rank: map(type) | time\n"]
        for _map, time, rank, team in sorted([
            [i.map, i.time, i.rank, i.team_rank]
            for i in usr.all_top_10s
        ], key=lambda x: x[2]):
            team = f'| {team}' if team is not None else ''
            list_top1s.append(f'{rank} {team}: {_map.map}({_map.server}) | {seconds_to_time(time)}')

        top1s = '\n'.join(list_top1s)
        if len(top1s) > 2000:
            return await im.send(player + '\n' + top1s)

        embed = Embed(
            title="player",
            description=top1s,
            color=im.user.color
        ).set_footer(text=f"{local.powered_by} {self.ddrace.powered()}")
        return await im.send(embed=embed)

    @ddnet.subcommand(name=clang.ddos.name,
                      description=clang.ddos.desc,
                      name_localizations=clang.ddos.name_lang,
                      description_localizations=clang.ddos.desc_lang)
    async def ddos(self, im: StormBotInter):
        im.func("ddnet ddos")
        await im.response.defer()

        status = await self.dd.status()
        if status is None:
            return await im.send(Types.RE)

        rows = [f'{FLAG_UNK} `server  | +- | ▲ pps | ▼ pps `']
        for server in status.servers:
            if server.packets_rx is None:
                server.packets_rx = -1
            if server.packets_tx is None:
                server.packets_tx = -1
            status = server_get_status_ddos(server, self.configs.ddnet)

            name = server.name.replace("DDNet ", '').upper()
            if "MASTER" not in name:
                name = country_size(name, 3)
            rows.append(f'{flag(name)} `{name:<8}|{status:^4}|'
                        f'{humanize_pps(server.packets_rx):>7}|'
                        f'{humanize_pps(server.packets_tx):>7}`')

        embed = Embed(
            title='Server Status',
            description='\n'.join(rows),
            url="https://ddnet.org/status/",
            timestamp=utcnow()
        )
        return await im.send(embed=embed)

    async def ddstats_request(self, im: StormBotInter, player: str, local: LangDDnet):
        await im.response.defer()

        usr = await self.ddrace.player(player)
        if usr is None:
            await im.send(Types.not_activity, format_=[self.ddrace.powered()])
            return
        return usr
