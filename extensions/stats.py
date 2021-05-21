from io import BytesIO

import discord
import matplotlib
import matplotlib.pyplot as plt
from discord.ext import commands
from jishaku.functools import executor_function
from matplotlib import ticker

from bot import Bot
from extensions.utils.scoresaber import ScoreSaberQueryConverter, get_profile

matplotlib.use('Agg')


@executor_function
def generate_chart(data) -> BytesIO:
    history = [int(point) for point in data['history'].split(",")]
    x_ticks = [num for num in range(len(history)) if num % 2 == 0]

    fig, ax = plt.subplots()

    ax.plot(history, linewidth=7)
    ax.set_title(data['playerName'] + '\'s ' + 'Rank Change', fontsize=30, fontweight='bold', loc='left', pad=15)

    ax.set_xlabel('Days Ago', fontsize=25, labelpad=7)
    ax.set_ylabel('Rank', fontsize=25, labelpad=7)

    ax.invert_yaxis()
    y_axis_diff = round(abs(history[0] - history[-1]) / 9)
    if y_axis_diff == 0:
        y_axis_diff += 1
    print(y_axis_diff)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(y_axis_diff))
    plt.yticks(fontsize=20)

    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f'-{i}' for i in x_ticks[::-1]])
    plt.xticks(fontsize=15)

    ax.margins(x=0.01, y=0.02)

    fig.set_figwidth(15)
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
    async def chart(self, ctx: commands.Context, query: ScoreSaberQueryConverter):
        buffer = await generate_chart(query['playerInfo'])
        file = discord.File(buffer, 'chart.png')
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Stats(bot))
