import re
from typing import Union
from urllib.parse import quote

from discord.ext import commands

from bot.bot import Bot

ss_link_regex = re.compile(r"https?:\/\/(?:(?:new)\.)?scoresaber\.com\/u\/(?P<id>[0-9]{16,20})")


async def scoresaber_id_from_query(ctx: commands.Context, query: str) -> tuple[bool, Union[int, str]]:
    query = quote(query.upper())
    async with ctx.bot.session.get(ctx.bot.api_url + "/players/by-name/" + query) as resp:
        data = await resp.json()
    return True, data['players'][0]['playerId']


class ScoreSaberQueryConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, query: str) -> int:
        if query.isdigit():
            return int(query)

        if url_match := ss_link_regex.match(query):
            return int(url_match['id'])

        worked, res = scoresaber_id_from_query(ctx, query)
        if worked:
            return res
        else:
            raise commands.BadArgument(res)


class Stats(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx: commands.Context, *, query: ScoreSaberQueryConverter):
        pass
