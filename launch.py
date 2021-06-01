import discord
from discord.ext import commands

import config
from bot import Bot


def callable_prefix(_, __):
    return commands.when_mentioned_or(*config.prefix)(_, __)


# initialize the bot
bot = Bot(command_prefix=callable_prefix, activity=config.activity, status=config.status)

if __name__ == "__main__":
    # only run the bot if this file is being run directly
    bot.load_extensions()
    bot.run(config.bot_token)
