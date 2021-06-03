import discord
from discord.ext import commands

from bot import Bot


class Misc(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def website(self, ctx: commands.Context):
        """Sends a link to Cube Community's website."""
        embed = discord.Embed(color=self.bot.cc_color)
        embed.description = "You can visit Cube Community's website [here](https://cube.community/main/home \"Cube Community's Website\")"
        await ctx.send(embed=embed)

    @commands.command()
    async def resources(self, ctx: commands.Context):
        """Sends a link to Cube Community's resources."""
        embed = discord.Embed(color=self.bot.cc_color)
        embed.description = "Cube Community has a bunch of resources you can use. You can find them [here](https://www.cube.community/main/resources/cc_files). Make sure to read the Info."
        await ctx.send(embed=embed)

    @commands.command()
    async def queryhelp(self, ctx: commands.Context):
        """Small command that gives an explanation of how to best use the bot."""
        message = """
This is a tutorial on how to effectively query users on Scoresaber with this bot. Usually you can tell if a command will be using this converter.
If you don't provide anything, as in you just use the command by itself, the bot will check if you have registered yourself. If you have, it will use you. If you haven't, it will let you know.
Mentioning a user will also check to see if that user is registered.\n
The best method is to send the url of the user whose profile you want to query.
You can also provide the user's Scoresaber ID. `https://scoresaber.com/u/< this is the id >&sort=2`\n
Lastly, you can just provide their username, and it will ask Scoresaber for their profile. This goes by the start of your name, so if your name is `LMAO | cooluser` and you give `cooluser` as input, it will not show up.
This is not recommended.
        """
        await ctx.send(embed=discord.Embed(description=message, color=self.bot.cc_color))


def setup(bot):
    bot.add_cog(Misc(bot))
