import asyncio
import logging
import random
from os import getcwd

import discord
import config
from aiohttp import ClientSession
from asyncpg import Pool, create_pool
from discord.ext import commands

# setup logging so we know wtf is going on with the bot
logger = logging.getLogger("bot")
logging.basicConfig(
    format="[{asctime}] {levelname:<7} {name}: {message}",  # you can change formatting if you want
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=logging.INFO,  # change this to logging.DEBUG if something is going wrong during startup
)


class Bot(commands.Bot):
    """Subclassed bot for added functionality and cleaner code"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()

        # the working directory for the bot, kinda hacky tho
        self.working_directory = getcwd().replace("\\", "/") + "/"

        # create a database connection
        self.pool: Pool = self.loop.run_until_complete(
            create_pool(dsn=config.postgres_dsn, loop=self.loop)
        )
        self.loop.create_task(self.__prep())

        # colors
        self.scoresaber_color = 0xFFDE1A
        self.cc_blue_color = 0x00AEEF
        self.cc_red_color = 0xEE283B

    async def __prep(self):
        # misc
        headers = {
            "User-Agent": f"Discord bot for the Cube Community discord server. discord.py version {discord.__version__}"
        }
        self.session = ClientSession(headers=headers)
        async with self.pool.acquire() as conn:
            with open(self.working_directory + "schema.sql") as f:
                await conn.execute(f.read())

    @property
    def cc_color(self):
        return random.choice((self.cc_red_color, self.cc_blue_color))

    def load_extensions(self):
        self.load_extension("jishaku")
        extensions = [
            "extensions.stats",
            "extensions.errorhandler",
            "extensions.leaderboards",
            "extensions.profile",
            "extensions.misc",
            "extensions.buttons",
        ]
        for ext in extensions:
            self.load_extension(ext)

    async def on_ready(self):
        """Lets us know when the bot is online. If you don't see this something went wrong"""
        message = (
            "Connected to Discord",
            "Username : {0}".format(self.user),
            "ID : {0.id}".format(self.user),
            f"Guilds : {len(self.guilds)}",
            f"Users : {len(self.users)}",
            f"Command Prefix : {self.command_prefix}",
        )
        for msg in message:
            logger.info(msg)

    async def close(self):
        await self.session.close()
        await super().close()
