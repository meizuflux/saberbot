import json
import re
from typing import Optional
from urllib.parse import quote

import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands, menus, tasks

from bot import Bot
from extensions.utils import ArgumentParser
from extensions.utils.menus import LeaderboardPages, LeaderboardSource, SongLeaderboardSource
from extensions.utils.scoresaber import LEADERBOARD_LINK_REGEX


class Leaderboards(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.hash_cache = {}
        self.generate_php_session_id.start()

    def cog_unload(self):
        if hasattr(self, 'session'):
            self.bot.loop.create_task(self.session.close())
        self.generate_php_session_id.stop()

    async def parse_song(self, query):
        if _hash := self.hash_cache.get(query):
            return _hash

        if re.match(r"([A-Z0-9]{40})", query):
            return query

        if LEADERBOARD_LINK_REGEX.match(query):
            async with self.bot.session.get(query) as resp:
                if not resp.ok:
                    raise commands.BadArgument("Invalid leaderboard url provided.")
                _hash = re.findall(r"<b>([A-Z0-9]{40})</b>", await resp.text())[0]

        if not _hash:
            async with self.bot.session.get("https://beatsaver.com/api/search/text?q=" + quote(query)) as resp:
                data = await resp.json()
                if songs := data['docs']:
                    for song in songs:
                        if song['metadata'].get('automapper') is None:
                            _hash = song['hash']
                            break
                if _hash is None:
                    raise commands.BadArgument("I could not find a song hash from your data.")
        self.hash_cache[query] = _hash
        return _hash.upper()

    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        menu = LeaderboardPages(delete_message_after=True)
        await menu.start(ctx)

    @commands.command()
    async def song_leaderboard(self, ctx: commands.Context, page: Optional[int], *, song: str):
        if not hasattr(self, 'session'):
            return await ctx.send("Bot is not prepped yet, check again soon.")
        query = song.strip()
        parser = ArgumentParser(allow_abbrev=False, add_help=False)
        parser.add_argument('data', nargs='*', default=None)
        parser.add_argument('-d', '--difficulty', nargs='+')
        parser.add_argument('-m', '--minimal', action='store_true')

        try:
            args = parser.parse_args(query.split())
        except RuntimeError as err:
            err = str(err).strip().capitalize()
            if err == 'Argument -d/--difficulty: expected at least one argument':
                err = "You provided the difficulty argument without providing a difficulty."
            return await ctx.send(err)
        diffs = {
            "expert+": "9",
            "expertplus": "9",
            "expert": "7",
            "hard": "5",
            "normal": "3",
            "easy": "1"
        }
        if not args.query:
            raise commands.BadArgument("You didn't provide a map.")
        if not args.difficulty:
            raise commands.BadArgument("You didn't provide a difficulty.")
        query = " ".join(args.query)
        diff = "".join(args.difficulty)
        difficulty = diffs.get(diff)
        if difficulty is None:
            raise commands.BadArgument(f"Difficulty '{diff}' is invalid.")
        await ctx.trigger_typing()
        _hash = await self.parse_song(query)
        if not page:
            page = 1
        url = f"https://scoresaber.com/game/scores-pc.php?levelId={_hash}&difficulty={difficulty}&gameMode=SoloStandard&page={page}"
        async with self.session.get(url) as resp:
            data = json.loads(await resp.text())
        url = 'https://scoresaber.com/leaderboard/' + data['uid']
        embed = discord.Embed(color=self.bot.scoresaber_color, description=data['ranked'], url=url)

        async with self.bot.session.get(url) as lb:
            soup = BeautifulSoup(await lb.text(), 'lxml')
        embed.title = soup.find('h4', {'class': 'title is-5'}).find_all('a')[0].text[:256]
        embed.set_thumbnail(url=soup.find_all('img')[1]['src'])
        things = [i.text.strip() for i in soup.find_all('b')[1:-1]]

        embed.set_author(name="Mapped By " + things.pop(0))
        mapping = {1: "Scores: ", 3: "Stars: ", 4: "Note Count: ", 5: "BPM: "}
        for index, i in enumerate(things):
            if fmt := mapping.get(index):
                embed.description += "\n" + fmt + str(i)

        pages = menus.MenuPages(source=SongLeaderboardSource(embed=embed, entries=data['scores'], per_page=4),
                                delete_message_after=True)
        await pages.start(ctx)

    @tasks.loop(hours=24)
    async def generate_php_session_id(self):
        if not hasattr(self, 'session'):
            self.session = aiohttp.ClientSession()
        data = {"playerid": 76561198045386379}
        await self.session.post("https://scoresaber.com/game/exchange.php", data=data)


def setup(bot):
    bot.add_cog(Leaderboards(bot))
