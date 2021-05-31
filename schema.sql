CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    scoresaber_id VARCHAR,
    pp DOUBLE PRECISION,
    change BIGINT,
    play_count JSONB, /* {"total": 41234, "ranked": 5342} */
    score JSONB, /* same thing as above */
    average_accuracy DOUBLE PRECISION,
    favorite_song JSONB DEFAULT '{"name": null, "url": null}'::jsonb, /* {"name": "Reality Check", "url": "url to song"} */
    favorite_saber JSONB DEFAULT '{"name": null, "url": null}'::jsonb, /* same format as above */
    headset VARCHAR,
    grip VARCHAR
);