-- PostgreSQL 초기화 스크립트
-- Dimension Tables

CREATE TABLE IF NOT EXISTS dim_player (
    player_id SERIAL PRIMARY KEY,
    nickname VARCHAR(50),
    tier VARCHAR(20),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_session (
    session_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES dim_player(player_id),
    game_mode VARCHAR(20),
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_time (
    time_id SERIAL PRIMARY KEY,
    event_time TIMESTAMP,
    day_of_week VARCHAR(10),
    day INT,
    week INT,
    month INT,
    year INT
);

-- Fact Table

CREATE TABLE IF NOT EXISTS fact_game_log (
    log_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES dim_session(session_id),
    player_id INT REFERENCES dim_player(player_id),
    time_id INT REFERENCES dim_time(time_id),
    event_type VARCHAR(50),
    damage INT,
    heal_amount INT,
    x INT,
    y INT
);
