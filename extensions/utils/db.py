from discord.ext import commands
from asyncpg import Pool


async def update_user_stats(snowflake: int, pool: Pool, data: dict) -> None:
    query = """
        WITH pre AS (
            INSERT INTO users (snowflake, id)
            VALUES ($1, $2)
            ON CONFLICT (snowflake)
            DO UPDATE
        )
        INSERT INTO stats
        VALUES ($2, $3, $4, $5, $6, $7, $8, $9, $10, $12, $13, $14, $15)
        ON CONFLICT (id)
        DO UPDATE
        """
    info = data["playerInfo"]
    score = data["scoreStats"]
    values = (
        snowflake,
        info["playerId"],
        info["playerName"],
        info["avatar"],
        info["country"],
        info["rank"],
        info["countryRank"],
        info["role"],
        [int(c) for c in info["history"].split(",")],
        score["averageRankedAccuracy"],
        score["totalScore"],
        score["totalRankedScore"],
        score["totalPlayCount"],
        score["rankedPlayCount"],
    )
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(query, *values)
