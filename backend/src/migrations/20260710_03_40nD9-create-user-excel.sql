-- create user_Excel
-- depends:


DROP TABLE IF EXISTS user_excel;

CREATE TABLE IF NOT EXISTS user_excel (
    id bigserial primary key,
    agent_code text NOT NULL,
    from_date date not null,
    to_date date not null,
    family_code text ,
    policy_holder text NOT NULL,
    policy_number text NOT NULL,
    DOB date NOT NULL,
    phone_number text NULL,
    email text NULL,
    Address text NULL,
    Agency_Code text Not NULL,
    Commecement_date date NOT NULL,
    plan integer NOT NULL,
    term integer NOT NULL,
    ppt integer NOT NULL,
    Sum_assured integer NOT NULL,
    Mode integer NOT NULL,
    fup_date date NOT NULL,
    premium integer NOT NULL,
    Nominee text NOT NULL,
    created_at timestamp with time zone default now(),
    created_by integer DEFAULT NULL,
    updated_at timestamp with time zone default now(),
    updated_by  bigint DEFAULT NULL,
    is_deleted boolean NOT NULL DEFAULT false

);

