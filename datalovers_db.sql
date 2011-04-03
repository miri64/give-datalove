DROP DATABASE IF EXISTS datalovers;
CREATE DATABASE IF NOT EXISTS datalovers;

CREATE TABLE IF NOT EXISTS datalovers.sessions (
    session_id      CHAR(128) NOT NULL UNIQUE,
    atime           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data            TEXT,
    UNIQUE INDEX    (session_id ASC),
    PRIMARY KEY     (session_id)
);

CREATE TABLE IF NOT EXISTS datalovers.history (
    sender          VARCHAR(23) NOT NULL,
    recipient       VARCHAR(23) NOT NULL,
    amount          INTEGER UNSIGNED NOT NULL DEFAULT 1,
    timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
                        ON UPDATE CURRENT_TIMESTAMP,
    INDEX (timestamp DESC),
    CONSTRAINT fk_sender
            FOREIGN KEY (sender)
            REFERENCES datalovers.users (nickname)
            ON DELETE CASCADE
            ON UPDATE RESTRICT,
    CONSTRAINT fk_recipient
            FOREIGN KEY (recipient)
            REFERENCES datalovers.users (nickname)
            ON DELETE CASCADE
            ON UPDATE RESTRICT
);

CREATE TABLE IF NOT EXISTS datalovers.user_sessions (
    nickname        VARCHAR(23) NOT NULL,
    session_id      CHAR(128) NOT NULL UNIQUE,
    PRIMARY KEY (nickname,session_id),
    UNIQUE INDEX (session_id ASC),
    CONSTRAINT fk_users_user_sessions
        FOREIGN KEY (nickname)
        REFERENCES datalovers.users (nickname)
        ON DELETE CASCADE
        ON UPDATE RESTRICT,
    CONSTRAINT fk_sessions_user_sessions
        FOREIGN KEY (session_id)
        REFERENCES datalovers.sessions (session_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS datalovers.user_websites (
    nickname        VARCHAR(23) NOT NULL,
    website         VARCHAR(50) NOT NULL,
    PRIMARY KEY (nickname,website),
    CONSTRAINT fk_users_user_websites
        FOREIGN KEY (nickname)
        REFERENCES datalovers.users(nickname)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);

CREATE TABLE IF NOT EXISTS datalovers.users (
    nickname        VARCHAR(23) NOT NULL,
    password        CHAR(64) NOT NULL,
    email           VARCHAR(50) DEFAULT NULL,
    available_love  BIGINT UNSIGNED NOT NULL,
    received_love   BIGINT UNSIGNED NOT NULL DEFAULT 0,
    last_changed    TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
                        ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX (nickname ASC),
    PRIMARY KEY (nickname)
);

