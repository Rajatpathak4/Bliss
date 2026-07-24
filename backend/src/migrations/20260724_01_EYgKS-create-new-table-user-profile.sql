-- create new_table user_profile
-- depends:



CREATE TABLE if not exists user_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    name Varchar(255) Not null,
    phone_number VARCHAR(15),
    role VARCHAR(50),
    company VARCHAR(100),
    location VARCHAR(100),
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);