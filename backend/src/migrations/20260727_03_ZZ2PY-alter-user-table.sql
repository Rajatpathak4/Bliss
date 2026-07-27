-- alter user table
-- depends: 


ALTER TABLE users ALTER COLUMN theme SET DEFAULT 'light';

UPDATE users SET theme = 'light' WHERE theme IS NULL;