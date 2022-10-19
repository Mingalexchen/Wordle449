DROP TABLE IF EXISTS UserInfo;
CREATE TABLE UserInfo (
    user_name VARCHAR NOT NULL primary key,
    user_password VARCHAR
);

DROP TABLE IF EXISTS GameStats;
CREATE TABLE GameStats (
    game_id INTEGER NOT NULL primary key AUTOINCREMENT,
    user_name VARCHAR NOT NULL,
    game_result INTEGER,  --0: in progress 1:win 2:lose
  	answer_attempted INTEGER,
    secret_word VARCHAR,
    attempt_1 VARCHAR,
    attempt_2 VARCHAR,
    attempt_3 VARCHAR,
    attempt_4 VARCHAR,
    attempt_5 VARCHAR,
    attempt_6 VARCHAR,
    FOREIGN KEY(user_name) REFERENCES UserInfo(user_name),
  	FOREIGN KEY(secret_word) REFERENCES SecretWords(secret_word)
);

DROP TABLE IF EXISTS SecretWords;
CREATE TABLE SecretWords (
    secret_word VARCHAR NOT NULL primary key
);

