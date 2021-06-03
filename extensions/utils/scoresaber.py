import re
from urllib.parse import quote

import discord
from discord.ext import commands

from extensions.utils.user import User

PROFILE_LINK_REGEX = re.compile(r"https?://(?:(?:new)\.)?scoresaber\.com/u/(?P<id>[0-9]{16,20})")
LEADERBOARD_LINK_REGEX = re.compile(r"https?://(?:(?:new)\.)?scoresaber\.com/leaderboard/[0-9]+")
DISCORD_MENTION_REGEX = mention_regex = re.compile(r"<@(!?)([0-9]*)>")
API_URL = "https://new.scoresaber.com/api"


async def scoresaber_id_from_query(ctx: commands.Context, query: str) -> User:
    """Function for getting a user by string"""
    query = quote(query.upper())
    async with ctx.bot.session.get(API_URL + "/players/by-name/" + query) as resp:
        data = await resp.json()
    try:
        return await get_profile(ctx, data["players"][0]["playerId"])
    except KeyError:
        # scoresaber makes error messages for us
        raise commands.BadArgument(data["error"]["message"])


async def get_profile(ctx: commands.Context, scoresaber_id: int) -> User:
    """Getting data from Scoresaber by an id."""
    url = API_URL + "/player/" + str(scoresaber_id) + "/full"
    await ctx.trigger_typing()
    async with ctx.bot.session.get(url) as resp:
        if not resp.ok:
            raise commands.BadArgument("Scoresaber returned a {0.status} status.".format(resp))
        data = await resp.json()
    return User.from_json(data)


async def scoresaber_id_from_user(ctx, user: discord.User):
    """Getting stats from the db."""
    data = await ctx.bot.pool.fetchrow("SELECT * FROM users WHERE snowflake = $1", user.id)
    if data is None:
        raise commands.BadArgument(
            "This user is not registered." if user != ctx.author else "You are not registered."
        )
    return User.from_psql(data)


class ScoreSaberQueryConverter(commands.Converter):
    """Converter for getting user data from input."""

    async def convert(self, ctx: commands.Context, query: str) -> User:
        if query is not None:
            # check lengths
            url_match = PROFILE_LINK_REGEX.match(query)
            if len(query) < 4 or len(query) > 31 and not url_match:
                raise commands.BadArgument("Please enter a data between 3 and 32 characters!")

        await ctx.trigger_typing()
        if not query:
            # get data from db
            return await scoresaber_id_from_user(ctx, ctx.author)

        if mention := DISCORD_MENTION_REGEX.fullmatch(query):
            # check if they mentioned a user
            try:
                user = await commands.UserConverter().convert(ctx, mention[0])
            except commands.UserNotFound:
                raise commands.BadArgument("You mentioned an invalid user.")
            return await scoresaber_id_from_user(ctx, user)

        if url_match:
            # check if the user sent a scoresaber link
            return await get_profile(ctx, int(url_match["id"]))

        return await scoresaber_id_from_query(ctx, query)
