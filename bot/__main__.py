import toml
from bot import Bot
from pathlib import Path
import time

# the working directory for the bot, kinda hacky tho
WORKING_DIRECTORY = str(Path(__file__).parent.parent).replace("\\", "/") + "/"

# load config files
with open(WORKING_DIRECTORY + "config.toml") as f:
    config = toml.loads(f.read())

# initialize the bot
bot = Bot(command_prefix=config['core']['prefix'])
bot.config = config

if __name__ == "__main__":
    # only run the bot if this file is being run directly
    bot.run(bot.config['core']['token'])
