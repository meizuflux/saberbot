import toml
from bot import Bot
from pathlib import Path
import logging

WORKING_DIRECTORY = str(Path(__file__).parent.parent).replace("\\", "/") + "/"
logger = logging.getLogger("bot")
logging.basicConfig(
    format="{asctime} {levelname:<7} {name:<15} |:| {message} |:| {pathname}:{lineno}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=logging.INFO
)

with open(WORKING_DIRECTORY + "config.toml") as f:
    config = toml.loads(f.read())

bot = Bot(command_prefix=config['core']['prefix'])
bot.config = config

if __name__ == "__main__":
    logger.info("Launching Bot")
    bot.run(bot.config['core']['token'])
