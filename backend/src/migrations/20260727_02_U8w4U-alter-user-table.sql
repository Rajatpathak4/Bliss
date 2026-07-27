-- alter user table
-- depends: 


ALTER TABLE users
ADD COLUMN IF NOT EXISTS theme VARCHAR(20);