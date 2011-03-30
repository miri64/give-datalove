DROP DATABASE IF EXISTS datalovers;
CREATE DATABASE IF NOT EXISTS datalovers;

CREATE TABLE IF NOT EXISTS datalovers.sessions (
    session_id	CHAR(128) NOT NULL,
    atime 		TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data 		TEXT,
    UNIQUE INDEX (session_id ASC),
    PRIMARY KEY (session_id)
);

CREATE TABLE IF NOT EXISTS `history` (
  `sender` varchar(23) NOT NULL,
  `recipient` varchar(23) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)

CREATE TABLE IF NOT EXISTS datalovers.users (
	nickname		VARCHAR(23) NOT NULL,
	password		CHAR(64) NOT NULL,
	email			VARCHAR(30) DEFAULT NULL,
	session_id		CHAR(128) DEFAULT NULL,
	available_love	BIGINT UNSIGNED NOT NULL,
	received_love	BIGINT UNSIGNED NOT NULL DEFAULT 0,
	last_changed	TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE 
					CURRENT_TIMESTAMP,
	UNIQUE INDEX (nickname ASC),
	PRIMARY KEY (nickname),
	UNIQUE INDEX fk_users_sessions (session_id ASC),
	CONSTRAINT fk_users_sessions
		FOREIGN KEY (session_id)
		REFERENCES datalovers.sessions (session_id)
    	ON DELETE SET NULL
		ON UPDATE CASCADE
);

