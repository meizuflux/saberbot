import re
from urllib.parse import quote

import discord
from discord.ext import commands

PROFILE_LINK_REGEX = re.compile(r"https?://(?:(?:new)\.)?scoresaber\.com/u/(?P<id>[0-9]{16,20})")
LEADERBOARD_LINK_REGEX = re.compile(r"https?://(?:(?:new)\.)?scoresaber\.com/leaderboard/[0-9]+")
DISCORD_MENTION_REGEX = mention_regex = re.compile(r"<@(!?)([0-9]*)>")
API_URL = "https://new.scoresaber.com/api"


async def scoresaber_id_from_query(ctx: commands.Context, query: str) -> dict:
    query = quote(query.upper())
    async with ctx.bot.session.get(API_URL + "/players/by-name/" + query) as resp:
        data = await resp.json()
    try:
        return await get_profile(ctx, data["players"][0]["playerId"])
    except KeyError:
        raise commands.BadArgument(data["error"]["message"])


async def get_profile(ctx: commands.Context, scoresaber_id: int) -> dict:
    url = API_URL + "/player/" + str(scoresaber_id) + "/full"
    await ctx.trigger_typing()
    async with ctx.bot.session.get(url) as resp:
        if not resp.ok:
            raise commands.BadArgument("Scoresaber returned a {0.status} status.".format(resp))
        data = await resp.json()
    return data


async def scoresaber_id_from_user(ctx, user: discord.User):
    scoresaber_id = await ctx.bot.pool.fetchval(
        "SELECT scoresaber_id FROM users WHERE user_id = $1", user.id
    )
    if scoresaber_id is None:
        raise commands.BadArgument(
            "This user is not registered." if user != ctx.author else "You are not registered."
        )
    return await get_profile(ctx, scoresaber_id)


class ScoreSaberQueryConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, query: str) -> dict:
        if query is not None:
            url_match = PROFILE_LINK_REGEX.match(query)
            if len(query) < 4 or len(query) > 31 and not url_match:
                raise commands.BadArgument("Please enter a data between 3 and 32 characters!")

        await ctx.trigger_typing()
        if not query:
            return await scoresaber_id_from_user(ctx, ctx.author)

        if mention := DISCORD_MENTION_REGEX.fullmatch(query):
            try:
                user = await commands.UserConverter().convert(ctx, mention[0])
            except commands.UserNotFound:
                raise commands.BadArgument("You mentioned an invalid user.")
            return await scoresaber_id_from_user(ctx, user)

        if url_match:
            return await get_profile(ctx, int(url_match["id"]))

        return await scoresaber_id_from_query(ctx, query)
