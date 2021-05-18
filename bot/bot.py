import logging
from discord.ext import commands

logger = logging.getLogger("bot")
logging.basicConfig(
    format="{asctime} {levelname:<7} {name} |:| {message} |:| {pathname}:{lineno}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=logging.INFO
)

class Bot(commands.Bot):
    async def on_ready(self):
        message = (
            "Connected to Discord",
            "Username : {0}".format(self.user),
            "ID       : {0.id}".format(self.user),
            f"Guilds   : {len(self.guilds)}",
            f"Users    : {len(self.users)}"
        )
        for msg in message:
            logger.info(msg)