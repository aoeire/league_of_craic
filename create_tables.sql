DROP TABLE IF EXISTS 'player_details';
DROP TABLE IF EXISTS 'match_details';

CREATE TABLE 'player_details' (
    'db_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'aoe2_id' INTEGER NOT NULL,
    'losses' INTEGER DEFAULT 0,
    'wins' INTEGER DEFAULT 0,
    'points' INTEGER DEFAULT 0,
    'username' TEXT NOT NULL,
    'hash' TEXT NOT NULL);

CREATE TABLE 'match_details' (
    'game_id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'game_ref' INTEGER,
    'player_1_id' INTEGER NOT NULL,
    'player_2_id' INTEGER NOT NULL,
    'player_1_name' TEXT NOT NULL,
    'player_2_name' TEXT NOT NULL,
    'player_1_civ' INTEGER,
    'player_2_civ' INTEGER,
    'player_1_rating' INTEGER,
    'player_2_rating' INTEGER);