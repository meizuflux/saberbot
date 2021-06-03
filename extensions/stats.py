from io import BytesIO

import discord
import matplotlib
import matplotlib.pyplot as plt
from discord.ext import commands
from jishaku.functools import executor_function
from matplotlib import ticker

from bot import Bot
from extensions.utils.scoresaber import ScoreSaberQueryConverter
from extensions.utils.user import User

matplotlib.use("Agg")


@executor_function
def generate_chart(user: User) -> BytesIO:
    history = user.history
    history.append(user.rank)  # update history
    x_ticks = [
        num for num in range(len(history) + 2) if num % 2 == 0
    ]  # we don't want everything for the x ticks

    fig, ax = plt.subplots()  # create a plot

    ax.plot(history, linewidth=7)
    ax.set_title(  # formatting
        user.name + "'s " + "Rank Change",
        fontsize=30,
        fontweight="bold",
        loc="left",
        pad=15,
    )

    # labels
    ax.set_xlabel("Days Ago", fontsize=25, labelpad=7)
    ax.set_ylabel("Rank", fontsize=25, labelpad=7)

    # y axis
    ax.invert_yaxis()
    plt.ticklabel_format(style="plain")
    plt.yticks(fontsize=20)

    # x axis
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"-{i}" for i in x_ticks[::-1]])  # reverse it
    plt.xticks(fontsize=15)

    ax.margins(x=0.01, y=0.02)  # make it tight

    # formatting
    fig.set_figwidth(16)
    fig.set_figheight(8)
    buffer = BytesIO()
    fig.savefig(buffer)
    buffer.seek(0)
    return buffer


class Stats(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def chart(self, ctx: commands.Context, *, query: str = None):
        await ctx.trigger_typing()
        user = await ScoreSaberQueryConverter().convert(ctx, query)
        buffer = await generate_chart(user)
        file = discord.File(buffer, "chart.png")  # convert bytes to a discord file
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Stats(bot))
