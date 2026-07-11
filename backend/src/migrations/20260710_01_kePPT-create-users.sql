-- create users
-- depends: 


DROP TABLE IF EXISTS users;

Create table if not exists users (
    id bigserial primary key ,
    name text not null,
    email text unique not null,
    password text not null,
    is_active boolean not null default false,
    created_at timestamp with time zone default now(),
    created_by integer DEFAULT NULL,
    updated_at timestamp with time zone default now(),
    updated_by  bigint DEFAULT NULL,
    is_deleted boolean NOT NULL DEFAULT false
);