-- create token
-- depends: 


DROP TABLE IF EXISTS token;

CREATE TABLE IF NOT EXISTS token (
    id bigserial primary key,
    token text unique not null,
    user_id bigint REFERENCES users(id) ON DELETE CASCADE,
    created_at timestamp with time zone default now(),
    expires_at timestamp with time zone not null
);