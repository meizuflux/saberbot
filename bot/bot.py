import asyncio
import logging
from discord.ext import commands
from asyncpg import create_pool

logger = logging.getLogger("bot")
logging.basicConfig(
    format="[{asctime}] {levelname:<7} {name}: {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=logging.INFO
)

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()
        self.pool = self.loop.run_until_complete(
            create_pool(port=5432, password='secret', database='bot', host='db', user='ppotatoo', loop=self.loop)
        )

    async def on_ready(self):
        message = (
            "Connected to Discord",
            "Username : {0}".format(self.user),
            "ID : {0.id}".format(self.user),
            f"Guilds : {len(self.guilds)}",
            f"Users : {len(self.users)}"
        )
        for msg in message:
            logger.info(msg)
