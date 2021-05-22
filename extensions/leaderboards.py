from discord.ext import commands, menus

from bot import Bot
from extensions.utils.menus import LeaderboardSource


class Leaderboards(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx: commands.Context, page: int = 1):
        url = "https://new.scoresaber.com/api/players/" + str(page)
        async with self.bot.session.get(url) as resp:
            data = await resp.json()
            if not data['players']:
                raise commands.BadArgument(f"The leaderboard for page {page} is empty.")
        pages = menus.MenuPages(source=LeaderboardSource(data['players'], per_page=5), delete_message_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(Leaderboards(bot))
