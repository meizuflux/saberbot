from math import ceil

import discord
from discord.ext import commands

from bot import Bot
from extensions.utils.scoresaber import ScoreSaberQueryConverter


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
            color=discord.Color.magenta(),
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


def setup(bot):
    bot.add_cog(Profile(bot))
