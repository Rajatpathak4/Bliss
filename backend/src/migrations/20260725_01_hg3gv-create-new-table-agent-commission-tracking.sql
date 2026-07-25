-- create new_table Agent commission tracking
-- depends:



CREATE TABLE IF NOT EXISTS policy_commission (
    id SERIAL PRIMARY KEY,
    policy_id INTEGER UNIQUE NOT NULL REFERENCES user_excel(id),
    commission_rate NUMERIC(5,2) DEFAULT 0,
    commission_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);