from math import ceil

import discord
from discord.ext import commands

from bot import Bot
from extensions.utils.scoresaber import ScoreSaberQueryConverter


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
        await self.view.message.delete()


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
        self.message = await self.ctx.send(embed=self.profile_embed, view=self)


class Profile(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx: commands.Context, query: ScoreSaberQueryConverter):
        data: dict = query
        player_info = data['playerInfo']
        score_stats = data['scoreStats']
        embed = discord.Embed(
            title=f"{player_info['playerName']}'s Profile",
            color=self.bot.scoresaber_color,
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

        await ctx.send(embed=embed)

    @commands.command()
    async def tp(self, ctx: commands.Context, *, query: ScoreSaberQueryConverter):
        query: dict
        view = ProfileView(data=query)
        view.add_item(MainButton(style=discord.ButtonStyle.primary, label="Stats"))
        view.add_item(FavoritesButton(style=discord.ButtonStyle.green, label="Favorites"))
        view.add_item(StopButton(style=discord.ButtonStyle.red, label="Stop"))
        await view.start(ctx)


def setup(bot):
    bot.add_cog(Profile(bot))
