from discord.ext import commands

import config
from bot import Bot
import os


if __name__ == "__main__":
    # only run the bot if this file is being run directly

    # prefix that gets called 
    def callable_prefix(_, __):
        return commands.when_mentioned_or(*config.prefix)(_, __)


    # initialize the bot
    bot = Bot(command_prefix=callable_prefix, activity=config.activity, status=config.status)

    # debug things
    os.environ['JISHAKU_NO_UNDERSCORE'] = "True"
    os.environ['JISHAKU_NO_DM_TRACEBACK'] = "True"
    os.environ['JISHAKU_HIDE'] = "True"

    bot.load_extensions()
    bot.run(config.bot_token)
