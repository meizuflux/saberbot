CREATE TABLE IF NOT EXISTS users (
    snowflake BIGINT PRIMARY KEY,
    id VARCHAR UNIQUE,
    song JSONB DEFAULT '{"name": null, "url": null}'::jsonb, /* {"name": "Reality Check", "url": "url to song"} */
    saber JSONB DEFAULT '{"name": null, "url": null}'::jsonb, /* same format as above */
    hmd VARCHAR,
    grip VARCHAR
);

CREATE TABLE IF NOT EXISTS stats (
    id VARCHAR UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    name TEXT,
    avatar VARCHAR,
    country CHAR(2),
    rank BIGINT,
    country_rank BIGINT,
    player_role TEXT DEFAULT null,
    history BIGINT[],

    avg_ranked_acc DOUBLE PRECISION, 
    total_score BIGINT,
    ranked_score BIGINT,
    total_played INT,
    ranked_played INT
)