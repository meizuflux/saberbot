from discord.ext import commands
from asyncpg import Pool


async def update_user_stats(snowflake: int, pool: Pool, data: dict) -> None:
    query = """
        INSERT INTO users (snowflake, id, name, avatar, country, pp, rank, country_rank, player_role, history, ranked_acc, total_score, ranked_score, total_played, ranked_played)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        ON CONFLICT (snowflake)
        DO UPDATE SET
            id = $2,
            name = $3,
            avatar = $4,
            country = $5,
            pp = $6,
            rank = $7,
            country_rank = $8,
            player_role = $9,
            history = $10,
            ranked_acc = $11,
            total_score = $12,
            ranked_score = $13,
            total_played = $14,
            ranked_played = $15
        """
    info = data["playerInfo"]
    score = data["scoreStats"]
    values = (
        snowflake,
        info["playerId"],
        info["playerName"],
        info["avatar"],
        info["country"],
        info["pp"],
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
