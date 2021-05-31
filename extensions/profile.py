import asyncio
from json import dumps
from math import ceil

import discord
from discord.ext import commands, tasks

from bot import Bot
from extensions.utils.scoresaber import ScoreSaberQueryConverter
from extensions.utils.user import User


class FavoritesButton(discord.ui.Button):
    view: 'ProfileView'

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.view.favorites_embed)


class MainButton(discord.ui.Button):
    view: 'ProfileView'

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.view.profile_embed)


class StopButton(discord.ui.Button):
    view: 'ProfileView'

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()


class ProfileView(discord.ui.View):
    def __init__(self, data: dict, *args, **kwargs):
        self.profile_data = data
        super().__init__(*args, **kwargs)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    @property
    def profile_embed(self):
        if not hasattr(self, '_profile_embed'):
            player_info = self.profile_data['playerInfo']
            score_stats = self.profile_data['scoreStats']
            embed = discord.Embed(
                title=f"{player_info['playerName']}'s Profile",
                color=self.ctx.bot.scoresaber_color,
                url="https://new.scoresaber.com/u/" + player_info['playerId']
            )
            embed.set_thumbnail(url="https://new.scoresaber.com" + player_info['avatar'])

            country_url = f"[#{player_info['countryRank']:,d}](https://scoresaber.com/global/{ceil(player_info['countryRank'] / 50)}&country={player_info['country']})"
            info_msg = (
                f"**PP:** {player_info['pp']}\n"
                f"**Rank:** [#{player_info['rank']:,d}](https://new.scoresaber.com/rankings/{ceil(player_info['rank'] / 50)})\n"
                f"**Country Rank:** :flag_{player_info['country'].lower()}: {country_url}"
            )
            if role := player_info['role']:
                info_msg += f"\n**Role:** {role}"
            embed.add_field(name="Player Info:", value=info_msg)

            score_msg = (
                f"**Average Ranked Accuracy:** {score_stats['averageRankedAccuracy']:.2f}\n"
                f"**Total Score:** {score_stats['totalScore']:,d}\n"
                f"**Total Ranked Score:** {score_stats['totalRankedScore']:,d}\n"
                f"**Total Play Count:** {score_stats['totalPlayCount']:,d}\n"
                f"**Ranked Play Count:** {score_stats['rankedPlayCount']:,d}"
            )
            embed.add_field(name="Score Stats:", value=score_msg, inline=False)
            self._profile_embed = embed
        return self._profile_embed

    @property
    def favorites_embed(self):
        if not hasattr(self, '_fav_embed'):
            embed = discord.Embed(color=self.ctx.bot.scoresaber_color)
            embed.description = 'this is a test for your favorites'
            self._fav_embed = embed
        return self._fav_embed

    async def start(self, ctx: commands.Context):
        self.ctx = ctx
        await self.ctx.send(embed=self.profile_embed, view=self)
        
        
class SettingView(discord.ui.View):
    editable = ("favorite_song", "favorite_saber", "headset", "grip")
    


class Profile(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.background_loop.start()
        
    def cog_unload(self):
        self.backround_loop.stop()

    @commands.command()
    async def profile(self, ctx: commands.Context, *, query: ScoreSaberQueryConverter):
        query: dict
        view = ProfileView(data=query)
        view.add_item(MainButton(style=discord.ButtonStyle.primary, label="Stats"))
        view.add_item(FavoritesButton(style=discord.ButtonStyle.green, label="Favorites"))
        view.add_item(StopButton(style=discord.ButtonStyle.red, label="Stop"))
        await view.start(ctx)

    def user_history(self, now: int, history: str) -> int:
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
        change = self.user_history(player_info['rank'], player_info['history'])
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
    async def register(self, ctx: commands.Context, *, user: ScoreSaberQueryConverter):
        await self.upsert_user_from_data(ctx.author.id, user)
        await ctx.send("Registered you into the database.")

    @tasks.loop(minutes=15)
    async def background_loop(self):
        counter = 0
        async with self.bot.pool.acquire() as conn:
            users = await conn.fetch("SELECT user_id, scoresaber_id FROM users")
            for user in users:
                if counter > 60:
                    counter = 0
                    await asyncio.sleep(60)
                _id = user['scoresaber_id']
                url = "https://new.scoresaber.com/api/players/" + _id + "/full"
                async with self.bot.session.get(url) as resp:
                    if not resp.ok:
                        print(resp)
                        print(resp.headers)
                        print(resp.status)
                    data = await resp.json()
                await self.upsert_user_from_data(user['user_id'], data)
                counter += 1
                

def setup(bot):
    bot.add_cog(Profile(bot))
