import discord
from discord.ext import commands

from bot import Bot


class AddButton(discord.ui.Button):
    view: 'SpeedView'

    async def callback(self, interaction: discord.Interaction):
        self.view.counter += 1
        await interaction.response.edit_message(content="Total Clicks: {0.counter}".format(self.view))

class SubtractButton(discord.ui.Button):
    view: 'SpeedView'

    async def callback(self, interaction: discord.Interaction):
        self.view.counter -= 1
        await interaction.response.edit_message(content="Total Clicks: {0.counter}".format(self.view))

class SpeedView(discord.ui.View):
    children: list[AddButton]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

class ButtonTesting(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context):
        view = SpeedView()
        view.add_item(SubtractButton(style=discord.ButtonStyle.danger, label="Subtract"))
        view.add_item(AddButton(style=discord.ButtonStyle.success, label="Add"))
        await ctx.send("Total Clicks: 0", view=view)

def setup(bot):
    bot.add_cog(ButtonTesting(bot))
