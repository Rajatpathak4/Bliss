-- alter user_excel_3
-- depends: 

ALTER TABLE public.user_excel
ALTER COLUMN family_code TYPE VARCHAR(20);

ALTER TABLE public.user_excel
ALTER COLUMN created_at TYPE TIMESTAMP;

ALTER TABLE public.user_excel
ALTER COLUMN updated_at TYPE TIMESTAMP;