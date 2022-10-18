PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS UserInfo;
CREATE TABLE UserInfo (
    user_id INTEGER NOT NULL primary key,
    user_name VARCHAR,
    user_password VARCHAR,
    UNIQUE(user_id)
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




INSERT INTO UserInfo(user_id, user_name, user_password) VALUES(000001,'Ming Chen','cpsc449');
INSERT INTO GameStats(game_id, user_id, game_result, answer_attempted, secret_word, attempt_1,
                      attempt_2) 
            VALUES(000001, 000001, 1, 2, 'Block','hello','Block');
INSERT INTO SecretWords(secret_word) VALUES('hello'),('Abuse'),('Adult'),('Agent'),('Anger'),('Apple'),
('Award'),('Basis'),('Beach'),('Birth'),('Block'),('Blood'),('Board'),('Brain'),('Bread'),('Break');

COMMIT;

