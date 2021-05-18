import toml
from bot import Bot
from pathlib import Path
import logging

WORKING_DIRECTORY = str(Path(__file__).parent.parent).replace("\\", "/") + "/"


with open(WORKING_DIRECTORY + "config.toml") as f:
    config = toml.loads(f.read())

bot = Bot(command_prefix=config['core']['prefix'])
bot.config = config

if __name__ == "__main__":
    bot.run(bot.config['core']['token'])
