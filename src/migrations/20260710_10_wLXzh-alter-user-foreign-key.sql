-- alter user_foreign_key
-- depends: 

ALTER TABLE public.user_excel
ADD COLUMN user_id INTEGER;

ALTER TABLE public.user_excel
ADD CONSTRAINT fk_user_excel_user
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE CASCADE;
