BEGIN;
INSERT INTO {{datalovers}}.auth_user (username, password, email, last_login, is_active, date_joined)
    SELECT nickname, password, email, last_changed, TRUE, last_changed
    FROM {{datalovers}}.users;

INSERT INTO {{datalovers}}.give_lovableobject (id, received_love)
    SELECT new.id, old.received_love
    FROM {{datalovers}}.users old 
        INNER JOIN {{datalovers}}.auth_user new 
            ON new.username = old.nickname;

INSERT INTO {{datalovers}}.give_dataloveprofile (lovableobject_ptr_id, user_id, available_love,last_love_update)
    SELECT new.id, new.id, old.available_love, old.last_changed
    FROM {{datalovers}}.users old 
        INNER JOIN {{datalovers}}.auth_user new 
            ON new.username = old.nickname;

INSERT INTO {{datalovers}}.give_datalovehistory (sender_id, recipient_id, amount, timestamp)
    SELECT sender.id, rec_id, old.amount, old.timestamp
    FROM {{datalovers}}.auth_user sender INNER JOIN {{datalovers}}.history old
                ON sender.username = old.sender
            INNER JOIN (    SELECT user.username AS rec_username, profile.lovableobject_ptr_id AS rec_id
                            FROM {{datalovers}}.auth_user user
                                INNER JOIN {{datalovers}}.give_dataloveprofile profile
                                    ON user.id = profile.user_id) receiver
                ON rec_username = old.recipient
    ORDER BY timestamp;

INSERT INTO {{datalovers}}.give_userwebsite (user_id, url)
    SELECT user.id, LOWER(website.website)
    FROM {{datalovers}}.user_websites website
        JOIN {{datalovers}}.auth_user user
            ON user.username = website.nickname;

DROP TABLE {{datalovers}}.user_websites;
DROP TABLE {{datalovers}}.user_sessions;
DROP TABLE {{datalovers}}.history;
DROP TABLE {{datalovers}}.users;
DROP TABLE {{datalovers}}.sessions;
COMMIT;
