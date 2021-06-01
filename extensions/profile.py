import asyncio
from json import dumps

import discord
from asyncpg import UniqueViolationError
from discord.ext import commands, tasks

from bot import Bot
from extensions.utils.buttons import MainButton, MiscButton, ProfileView, SettingView, StopButton
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
            users = await conn.fetch("SELECT user_id, scoresaber_id FROM users")
            for user in users:
                if counter > 60:
                    counter = 0
                    await asyncio.sleep(60)
                _id = user['scoresaber_id']
                url = "https://new.scoresaber.com/api/player/" + _id + "/full"
                async with self.bot.session.get(url) as resp:
                    if not resp.ok:
                        print(resp)
                        print(resp.headers)
                        print(resp.status)
                        continue
                    data = await resp.json()
                await self.upsert_user_from_data(user['user_id'], data)
                counter += 1

    @staticmethod
    def calc_change(now: int, history: str) -> int:
        history = history.split(",")
        index = 7
        if len(history) < 7:
            index = len(history)
        return int(history[-index]) - now

    async def upsert_user_from_data(self, user_id: int, data: dict):
        player_info = data['playerInfo']
        score_stats = data['scoreStats']

        scoresaber_id = player_info['playerId']
        pp = player_info['pp']
        change = self.calc_change(player_info['rank'], player_info['history'])
        play_count = dumps({"total": score_stats['totalPlayCount'], "ranked": score_stats['rankedPlayCount']})
        score = dumps({"total": score_stats['totalScore'], "ranked": score_stats['totalRankedScore']})
        average_accuracy = score_stats['averageRankedAccuracy']

        query = (
            """
            INSERT INTO
                users (user_id, scoresaber_id, pp, change, play_count, score, average_accuracy)
            VALUES
                ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (user_id)
                DO UPDATE
                    SET
                        scoresaber_id = $2,
                        pp = $3,
                        change = $4,
                        play_count = $5,
                        score = $6,
                        average_accuracy = $7
            """
        )
        values = (user_id, scoresaber_id, pp, change, play_count, score, average_accuracy)
        await self.bot.pool.execute(query, *values)

    @commands.command()
    async def profile(self, ctx: commands.Context, *, query=None):
        data: dict = await ScoreSaberQueryConverter().convert(ctx, query)
        view = ProfileView(data=data)
        registered = await self.bot.pool.fetchval("SELECT True FROM users WHERE scoresaber_id = $1",
                                                  data['playerInfo']['playerId'])
        if registered is not None:
            view.add_item(MainButton(style=discord.ButtonStyle.blurple, label="Stats"))
            view.add_item(MiscButton(style=discord.ButtonStyle.green, label="Misc"))

        view.add_item(StopButton())
        await view.start(ctx)

    @commands.command()
    async def register(self, ctx: commands.Context, *, user: ScoreSaberQueryConverter):
        try:
            await self.upsert_user_from_data(ctx.author.id, user)
        except UniqueViolationError:
            player_id = user['playerInfo']['playerId']
            user_id = await self.bot.pool.fetchval("SELECT user_id FROM users WHERE scoresaber_id = $1", player_id)
            return await ctx.send(
                f"{(await self.bot.fetch_user(user_id)).mention} already has registered themselves with this user.",
                allowed_mentions=discord.AllowedMentions.none())
        await ctx.send("Registered you into the database.")

    @commands.command(name='set', aliases=('update',))
    async def _set(self, ctx: commands.Context):
        msg = f"Please click the button with the name that resembles the item you want to {ctx.invoked_with}."
        embed = discord.Embed(title=f"Editing your profile.", description=msg, color=self.bot.cc_color)
        await ctx.send(embed=embed, view=SettingView(ctx))


def setup(bot):
    bot.add_cog(Profile(bot))
