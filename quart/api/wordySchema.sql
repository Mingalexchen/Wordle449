DROP TABLE IF EXISTS UserInfo;
CREATE TABLE UserInfo (
    user_id INTEGER NOT NULL primary key AUTOINCREMENT,
    user_name VARCHAR NOT NULL UNIQUE,
    user_password VARCHAR
);

DROP TABLE IF EXISTS GameStats;
CREATE TABLE GameStats (   
    game_id INTEGER NOT NULL primary key,
    user_id VARCHAR,
    game_result INTEGER,  --0: in progress 1:win 2:lose
  	answer_attempted INTEGER,
    secret_word VARCHAR,
    attempt_1 VARCHAR,
    attempt_2 VARCHAR,
    attempt_3 VARCHAR,
    attempt_4 VARCHAR,
    attempt_5 VARCHAR,
    attempt_6 VARCHAR,
  	UNIQUE(game_id),
  	FOREIGN KEY(user_id) REFERENCES UserInfo(user_id)
  	FOREIGN KEY(secret_word) REFERENCES SecretWords(secret_word)
);

DROP TABLE IF EXISTS SecretWords;
CREATE TABLE SecretWords (
    secret_word VARCHAR NOT NULL primary key,
    UNIQUE(secret_word)
);

DROP TABLE IF EXISTS SecretWords;
CREATE TABLE SecretWords (
    secret_id INTEGER NOT NULL primary key,
    secret_word VARCHAR NOT NULL
);

DROP TABLE IF EXISTS ValidSecretWords;
CREATE TABLE ValidSecretWords (
    valid_id INTEGER NOT NULL primary key,
    valid_word VARCHAR NOT NULL
);

DROP TABLE IF EXISTS ValidSecretWords;
CREATE TABLE ValidSecretWords (
    valid_id INTEGER NOT NULL primary key,
    valid_word VARCHAR NOT NULL
);
