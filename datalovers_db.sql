DROP DATABASE IF EXISTS datalovers;
CREATE DATABASE IF NOT EXISTS datalovers;

CREATE TABLE IF NOT EXISTS datalovers.sessions (
    session_id      CHAR(128) NOT NULL,
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
    PRIMARY KEY (sender,recipient,timestamp),
    CONSTRAINT fk_sender
            FOREIGN KEY (sender)
            REFERENCES datalovers.users (nickname)
            ON DELETE SET NULL
            ON UPDATE CASCADE,
    CONSTRAINT fk_recipient
            FOREIGN KEY (recipient)
            REFERENCES datalovers.users (nickname)
            ON DELETE SET NULL
            ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS datalovers.users (
    nickname        VARCHAR(23) NOT NULL,
    password        CHAR(64) NOT NULL,
    email            VARCHAR(30) DEFAULT NULL,
    session_id        CHAR(128) DEFAULT NULL,
    available_love    BIGINT UNSIGNED NOT NULL,
    received_love    BIGINT UNSIGNED NOT NULL DEFAULT 0,
    last_changed    TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
                        ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX (nickname ASC),
    PRIMARY KEY (nickname),
    UNIQUE INDEX fk_users_sessions (session_id ASC),
    CONSTRAINT fk_users_sessions
        FOREIGN KEY (session_id)
        REFERENCES datalovers.sessions (session_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

