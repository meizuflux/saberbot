CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    scoresaber_id BIGINT,
    pp DOUBLE PRECISION,
    rank BIGINT,
    favorite_song JSONB,
    favorite_saber JSONB,
)