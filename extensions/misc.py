import discord
from discord.ext import commands

from bot import Bot


class Misc(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def website(self, ctx: commands.Context):
        embed = discord.Embed(color=self.bot.cc_color)
        embed.description = "You can visit Cube Community's website [here](https://cube.community/main/home \"Cube Community's Website\")"
        await ctx.send(embed=embed)

    @commands.command()
    async def resources(self, ctx: commands.Context):
        embed = discord.Embed(color=self.bot.cc_color)
        embed.description = "Cube Community has a bunch of resources you can use. You can find them [here](https://www.cube.community/main/resources/cc_files). Make sure to read the Info."
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Misc(bot))