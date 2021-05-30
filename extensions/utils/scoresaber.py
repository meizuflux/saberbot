import re
from urllib.parse import quote

from discord.ext import commands

PROFILE_LINK_REGEX = re.compile(r"https?:\/\/(?:(?:new)\.)?scoresaber\.com\/u\/(?P<id>[0-9]{16,20})")
LEADERBOARD_LINK_REGEX = re.compile(r"https?:\/\/(?:(?:new)\.)?scoresaber\.com\/leaderboard\/[0-9]+")
API_URL = "https://new.scoresaber.com/api"


async def scoresaber_id_from_query(ctx: commands.Context, query: str) -> dict:
    query = quote(query.upper())
    async with ctx.bot.session.get(API_URL + "/players/by-name/" + query) as resp:
        data = await resp.json()
    try:
        return await get_profile(ctx, data['players'][0]['playerId'])
    except KeyError:
        raise commands.BadArgument(data['error']['message'])


async def get_profile(ctx: commands.Context, scoresaber_id: int) -> dict:
    url = API_URL + "/player/" + str(scoresaber_id) + "/full"
    await ctx.trigger_typing()
    async with ctx.bot.session.get(url) as resp:
        data = await resp.json()
    return data


class ScoreSaberQueryConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, query: str) -> dict:
        url_match = PROFILE_LINK_REGEX.match(query)
        if len(query) < 4 or len(query) > 31 and not url_match:
            raise commands.BadArgument("Please enter a query between 3 and 32 characters!")

        await ctx.trigger_typing()
        if url_match:
            return await get_profile(ctx, int(url_match['id']))

        return await scoresaber_id_from_query(ctx, query)
