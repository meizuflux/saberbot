from io import BytesIO

import discord
import matplotlib
import matplotlib.pyplot as plt
from discord.ext import commands
from jishaku.functools import executor_function
from matplotlib import ticker

from bot import Bot
from extensions.utils.scoresaber import ScoreSaberQueryConverter

matplotlib.use("Agg")


@executor_function
def generate_chart(data) -> BytesIO:
    history = [int(point) for point in data["history"].split(",")]
    history.append(data["rank"])
    x_ticks = [num for num in range(len(history) + 2) if num % 2 == 0]

    fig, ax = plt.subplots()

    ax.plot(history, linewidth=7)
    ax.set_title(
        data["playerName"] + "'s " + "Rank Change",
        fontsize=30,
        fontweight="bold",
        loc="left",
        pad=15,
    )

    ax.set_xlabel("Days Ago", fontsize=25, labelpad=7)
    ax.set_ylabel("Rank", fontsize=25, labelpad=7)

    ax.invert_yaxis()
    plt.ticklabel_format(style="plain")
    plt.yticks(fontsize=20)

    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"-{i}" for i in x_ticks[::-1]])
    plt.xticks(fontsize=15)

    ax.margins(x=0.01, y=0.02)

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
    async def stats(self, ctx: commands.Context, *, query: ScoreSaberQueryConverter):
        pass

    @commands.command()
    async def chart(self, ctx: commands.Context, *, query: str = None):
        await ctx.trigger_typing()
        data = await ScoreSaberQueryConverter().convert(ctx, query)
        buffer = await generate_chart(data["playerInfo"])
        file = discord.File(buffer, "chart.png")
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Stats(bot))
