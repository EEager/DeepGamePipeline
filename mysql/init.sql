CREATE DATABASE IF NOT EXISTS gamelogs;
-- 데이터베이스를 생성하고 명시적으로 연결
ALTER DATABASE gamelogs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 다시 데이터베이스 지정
USE gamelogs;


CREATE TABLE IF NOT EXISTS logs_attack (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    target_id INT,
    damage INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs_heal (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    heal_amount INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs_move (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    x INT,
    y INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs_transformed (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(255),
    x VARCHAR(255),
    y VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS player_summary (
    player_id INT PRIMARY KEY,
    move_count INT,
    attack_count INT,
    total_damage INT,
    heal_count INT,
    total_heal INT
);

