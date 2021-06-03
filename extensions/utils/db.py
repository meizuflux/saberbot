from discord.ext import commands
from asyncpg import Pool


async def update_user_stats(snowflake: int, pool: Pool, data: dict) -> None:
    query = """
        WITH pre AS (
            INSERT INTO users (snowflake, id)
            VALUES ($1, $2)
            ON CONFLICT (snowflake)
            DO UPDATE
            SET snowflake = $1, id = $2
        )
        INSERT INTO stats
        VALUES ($2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        ON CONFLICT (id)
        DO UPDATE SET
            id = $2,
            name = $3,
            avatar = $4,
            country = $5,
            rank = $6,
            country_rank = $7,
            player_role = $8,
            history = $9,
            avg_ranked_acc = $10,
            total_score = $11,
            ranked_score = $12,
            total_played = $13,
            ranked_played = $14
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
