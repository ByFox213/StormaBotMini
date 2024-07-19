import logging
from os import getcwd

import nextcord
from PIL.ImageFont import FreeTypeFont
from ddapi import DDnetApi, DDstats, DDPlayer, Master
from nextcord import SlashOption, Embed, Color, Interaction, Locale
from nextcord.ext import commands
from PIL import ImageFont
from nextcord.utils import utcnow

from StormaLibs import seconds_to_hour, get_files, nickname, generate_profile_image, seconds_to_time, humanize_pps, server_get_status_ddos, send_query, flag, FLAG_UNK, text_to_file

DIR = f"{getcwd()}/data/assets"


class DDnet(commands.Cog):
    def __init__(self):
        self.ready: bool = False
        self.dd: DDnetApi = DDnetApi()
        self.ddrace: DDstats = DDstats()
        self.PPS_THRESHOLD: int = 10000
        self.PPS_RATIO_MIN: int = 1000
        self.PPS_RATIO_THRESHOLD: float = 2.5
        self.font_normal: FreeTypeFont = ImageFont.truetype(f'{DIR}/fonts/normal.ttf', 24)
        self.font_bold: FreeTypeFont = ImageFont.truetype(f'{DIR}/fonts/bold.ttf', 34)
        self.font_big: FreeTypeFont = ImageFont.truetype(f'{DIR}/fonts/bold.ttf', 48)
        self.thresholds: dict[int, tuple] = {
            18000: ('18k', (184, 81, 50)),
            17000: ('17k', (156, 162, 142)),
            16000: ('16k', (156, 162, 142)),
            15000: ('15k', (156, 162, 142)),
            14000: ('14k', (86, 79, 81)),
            10000: ('10k', (122, 32, 43)),
            8000: ('8k', (196, 172, 140)),
            7000: ('7k', (148, 156, 161)),
            6000: ('6k', (161, 140, 148)),
            5000: ('5k', (229, 148, 166)),
            4000: ('4k', (183, 188, 198)),
            3000: ('3k', (60, 76, 89)),
            2000: ('2k', (145, 148, 177)),
            1000: ('1k', (108, 12, 12)),
            1: ('1+', (148, 167, 75)),
            0: ('0', (156, 188, 220)),
        }
        self.flags = get_files(f"{DIR}/flags")
        self.profile_backgrounds = get_files(f"{DIR}/profile_backgrounds")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.ready:
            print(f"| bot is running")
            logging.info(f"bot is running")
            self.ready: bool = True

    @nextcord.slash_command(name="ddnet")
    async def ddnet(self, im: Interaction):
        pass

    @ddnet.subcommand(name="profile",
                      description="generates a user profile picture",
                      name_localizations={Locale.ru: "профиль"})
    async def profile(self, im: Interaction, player: str = nickname):
        data: DDPlayer = await self.dd.player(player)
        if data is None:
            return await send_query(player, im, await self.dd.query(player))
        await im.client.loop.create_task(generate_profile_image(self, data, im))

    @ddnet.subcommand(name="playtime", description="показывает, сколько игрок сыграл на картах и в целом")
    async def playtime(self, im: Interaction, player: str = nickname):
        usr = await self.ddrace.player(player)
        if usr is None:
            return await send_query(player, im, await self.dd.query(player))
        if usr.most_played_categories is None or usr.most_played_maps is None or usr.most_played_gametypes is None:
            return await im.send(embed=Embed(title="Ошибка запроса", description="некоторые компоненты для создания недостаточны или отсутствуют", color=Color.red()))
        maps = sorted([(i.map_name, i.seconds_played) for i in usr.most_played_maps[:15]], key=lambda h: h[1], reverse=True)
        f1 = max([len(i[0]) for i in maps] + [20]) + 2
        s1 = '\n'.join([f"{i:<{f1}}{seconds_to_hour(o)}" for i, o in maps])
        s2 = '\n'.join([f"{i:<{f1}}{seconds_to_hour(o)}" for i, o in sorted([(i.key, i.seconds_played) for i in usr.most_played_categories], key=lambda h: h[1], reverse=True)])
        embed = Embed(title=f"Показывает общее время игры игрока, ``{player}``", color=im.user.color)
        embed.add_field(name=f"``` {'Карта{0}Время игры (часы)'.format(' ' * (f1 - 2))}```", value=f"```{s1}```", inline=False)
        embed.add_field(name=f"``` {'Категория{0}Время игры (часы)'.format(' ' * (f1 - 6))}```", value=f"```{s2}```", inline=False)
        embed.add_field(name="``` Общее время игры (часы)```", value=f"```{seconds_to_hour(sum([i.seconds_played for i in usr.most_played_gametypes]))}```", inline=False)
        del maps, s1, s2, f1, usr
        return await im.send(embed=embed)

    @ddnet.subcommand(name='find', description="определяет, на каких серверах присутствует данный игрок")
    async def ddnet_find(self, im: Interaction, player: str = nickname):
        servers: Master = await self.dd.master()
        count_server: int = servers.get_count()
        count: int = 1
        find: list = []
        async for info in servers.get_info():
            for user in info.clients:
                if user.name == player:
                    find.append(f"{count}. Сервер: {info.name}: {info.map.get('name', '')}")
                    count += 1
        if len(find) == 0:
            return await im.send(embed=Embed(title='Игрок не найден', color=im.user.color), ephemeral=True)
        pl: str = "\n".join(find)
        embed: Embed = Embed(title='{1} найден на {0} серверах:'.format(count - 1, player),
                             color=im.user.color,
                             description=pl)
        embed.set_footer(text=f"Количество обработанных серверов: {count_server}")
        return await im.send(embed=embed)

    @ddnet.subcommand(name="map_claimed", description="отображает количество пройденных карт максимум до 10 штук")
    async def ddnet_map_claimed(self, im: Interaction, player: str = nickname,
                                limit: int = SlashOption(required=False, default=20, max_value=100)):
        usr = await self.dd.player(player)
        if usr is None:
            return await send_query(player, im, await self.dd.query(player))
        maps = []
        for typ, p in usr.types.model_dump().items():
            if p is None:
                continue
            for map_name, data in p.get("maps").items():
                if data is None:
                    continue
                maps.append((map_name, data.get("finishes")))
        maps = sorted(maps, key=lambda x: x[1], reverse=True)[:limit]
        desk = "\n".join(f"``{map_name}``:  {count}" for map_name, count in maps)
        if len(desk) > 2000:
            desk = f"количество пройденных карт\n\n" + desk.replace('`', '')
            return await im.send(file=text_to_file(desk))
        embed = Embed(title="количество пройденных карт",
                      description=desk,
                      color=Color.purple())
        embed.set_footer(text=f"{player}{usr.emoji}")
        return await im.send(embed=embed)

    @ddnet.subcommand(name="clans", description="Отображает информацию о кланах")
    async def ddnet_clans(self, im: Interaction, count: int = SlashOption(name="count", min_value=10, max_value=250, default=None, required=False)):
        if count is None:
            count = 10
        master: Master = await self.dd.master()
        dat = master.get_clans(count)
        lis = [f"``{count}``, ``{n}``, {o}" for count, (n, o) in enumerate(dat, 1)]
        desk = 'Топ, клан, онлайн\n' + "\n".join(lis)
        if len(desk) > 2000:
            desk = f"Кланы: {count}\n\n" + desk.replace('`',  '')
            return await im.send(file=text_to_file(desk))
        embed = Embed(title=f"Кланы: {count}", description=desk, color=im.user.color)
        return await im.send(embed=embed)

    @ddnet.subcommand(name="clan", description="Отображает информацию о клане и показывает сыгранных людей в этом клане не более 100")
    async def ddnet_clan(self, im: Interaction,  clan: str = SlashOption(name="clan")):
        master: Master = await self.dd.master()
        clients = [(info.name, client.name) async for info in master.get_info() for client in info.clients if
                   client.clan == clan]
        clients_str, e = '', ''
        for server_name, client_name in clients[:100]:
            if e != server_name:
                e = server_name
                clients_str += f'\n{server_name}:\n'
            clients_str += f'``{client_name}``\n'
        desk = f"Number of online participants: {len(clients)}\n\n{clients_str}"
        if len(desk) > 2000:
            return await im.send(f"Clan: {clan}\n\n" + desk.replace('``', ''))
        embed = Embed(title=f"Clan: {clan}",
                      description=desk,
                      color=im.user.color)
        return await im.send(embed=embed)

    @ddnet.subcommand(name="top_1s", description="Выводит все карты в которых рекорд меньше или равняется 10")
    async def top_1s(self, im: Interaction, player: str = nickname):
        usr = await self.ddrace.player(player)
        if usr is None:
            return await send_query(player, im, await self.dd.query(player))
        top10 = ["ранг | командный ранг: карта(тип) | время\n"]
        for _map, time, rank, team in sorted([[i.map, i.time, i.rank, i.team_rank] for i in usr.all_top_10s], key=lambda x: x[2]):
            team = '' if team is None else f'| {team}'
            top10.append(f'{rank} {team}: {_map.map}({_map.server}) | {seconds_to_time(time)}')
        top10 = '\n'.join(top10)
        if len(top10) > 2000:
            return await im.send(file=text_to_file(player + '\n' + top10))
        embed = Embed(title=player, description=top10, color=im.user.color)
        return await im.send(embed=embed)

    @ddnet.subcommand(name="ddos", description="Отображает состояние серверов")
    async def ddos(self, im: Interaction):
        status = await self.dd.status()
        if status is None:
            return await im.send(embed=Embed(title="Ошибка запроса", color=Color.red()))
        rows = [f'{FLAG_UNK} `server| +- | ▲ pps | ▼ pps `']
        for server in status.servers:
            if server.packets_rx is None:
                server.packets_rx = -1
            if server.packets_tx is None:
                server.packets_tx = -1
            status = server_get_status_ddos(server, self.PPS_THRESHOLD, self.PPS_RATIO_MIN, self.PPS_RATIO_THRESHOLD)
            name = server.name.replace("DDNet ", '').upper()
            if name != "MASTER":
                num = ''
                if len(name) > 3 and name[3].isnumeric():
                    num = name[3]
                name = name[:3] + num
            rows.append(f'{flag(name)} `{name:<6}|{status:^4}|{humanize_pps(server.packets_rx):>7}|{humanize_pps(server.packets_tx):>7}`')
        embed = Embed(title='Server Status', description='\n'.join(rows), url="https://ddnet.org/status/", timestamp=utcnow())
        return await im.send(embed=embed)
