import asyncio

import discord
from asyncpg import UniqueViolationError
from discord.ext import commands, tasks

from bot import Bot
from extensions.utils.buttons import MainButton, MiscButton, ProfileView, SettingView, StopButton
from extensions.utils.db import update_user_stats
from extensions.utils.scoresaber import ScoreSaberQueryConverter


class Profile(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.background_loop.start()

    def cog_unload(self):
        self.background_loop.stop()

    @tasks.loop(minutes=15)
    async def background_loop(self):
        await self.bot.wait_until_ready()
        counter = 0
        async with self.bot.pool.acquire() as conn:
            users = await conn.fetch("SELECT snowflake, id FROM users")
            for user in users:
                if counter > 60:
                    counter = 0
                    await asyncio.sleep(60)
                url = "https://new.scoresaber.com/api/player/" + user["id"] + "/full"
                async with self.bot.session.get(url) as resp:
                    if not resp.ok:
                        print(resp)
                        print(resp.headers)
                        print(resp.status)
                        continue
                    data = await resp.json()
                await update_user_stats(user["snowflake"], self.bot.pool, data)
                counter += 1

    @commands.command()
    async def profile(self, ctx: commands.Context, *, query=None):
        user = await ScoreSaberQueryConverter().convert(ctx, query)
        view = ProfileView(user=user)
        registered = await self.bot.pool.fetchval(
            "SELECT True FROM users WHERE id = $1", user.id
        )
        if registered is not None:
            view.add_item(MainButton(style=discord.ButtonStyle.blurple, label="Stats"))
            view.add_item(MiscButton(style=discord.ButtonStyle.green, label="Misc"))

        view.add_item(StopButton())
        await view.start(ctx)

    @commands.command()
    async def register(self, ctx: commands.Context, *, user: ScoreSaberQueryConverter):
        try:
            await update_user_stats(ctx.author.id, self.bot.pool, user.to_json())
        except UniqueViolationError:
            player_id = user.id
            user_id = await self.bot.pool.fetchval(
                "SELECT snowflake FROM users WHERE id = $1", player_id
            )
            return await ctx.send(
                f"{(await self.bot.fetch_user(user_id)).mention} already has registered themselves with this user.",
                allowed_mentions=discord.AllowedMentions.none(),
            )
        await ctx.send("Registered you into the database.")

    @commands.command(name="set", aliases=("update",))
    async def _set(self, ctx: commands.Context):
        msg = f"Please click the button with the name that resembles the item you want to {ctx.invoked_with}."
        embed = discord.Embed(
            title=f"Editing your profile.", description=msg, color=self.bot.cc_color
        )
        await ctx.send(embed=embed, view=SettingView(ctx))


def setup(bot):
    bot.add_cog(Profile(bot))
