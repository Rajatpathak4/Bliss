-- alter user_excel_2
-- depends: 


ALTER TABLE public.user_excel ALTER COLUMN policy_number TYPE VARCHAR USING policy_number::VARCHAR;
ALTER TABLE public.user_excel ALTER COLUMN phone_number TYPE VARCHAR USING phone_number::VARCHAR;
