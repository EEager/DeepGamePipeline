CREATE DATABASE IF NOT EXISTS gamelogs;
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

