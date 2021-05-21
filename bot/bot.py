import asyncio
import logging
from pathlib import Path

import toml
from asyncpg import create_pool
from discord.ext import commands

# setup logging so we know wtf is going on with the bot
logger = logging.getLogger("bot")
logging.basicConfig(
    format="[{asctime}] {levelname:<7} {name}: {message}",  # you can change formatting if you want
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=logging.INFO  # change this to logging.DEBUG if something is going wrong during startup
)


class Bot(commands.Bot):
    """Subclassed bot for added functionality and cleaner code"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()

        # the working directory for the bot, kinda hacky tho
        self.working_directory = str(Path(__file__).parent.parent).replace("\\", "/") + "/"

        # load config files
        with open(self.working_directory + "config.toml") as f:
            self.config = toml.loads(f.read())

        # create a database connection
        self.pool = self.loop.run_until_complete(
            create_pool(dsn=self.config['core']['postgres_dsn'], loop=self.loop)
        )

        # misc
        self.api_url = "https://new.scoresaber.com/api"

    async def on_ready(self):
        """Lets us know when the bot is online. If you don't see this something went wrong"""
        message = (
            "Connected to Discord",
            "Username : {0}".format(self.user),
            "ID : {0.id}".format(self.user),
            f"Guilds : {len(self.guilds)}",
            f"Users : {len(self.users)}",
            f"Command Prefix : {self.command_prefix}"
        )
        for msg in message:
            logger.info(msg)
