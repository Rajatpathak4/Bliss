-- alter user_excel
-- depends:


ALTER TABLE public.user_excel
ALTER COLUMN family_code TYPE VARCHAR USING family_code::VARCHAR;