-- alter user_excel_4
-- depends: 

ALTER TABLE public.user_excel
ALTER COLUMN mode TYPE VARCHAR(5) USING mode::VARCHAR;
ALTER TABLE public.user_excel ALTER COLUMN sum_assured TYPE NUMERIC(14,2) USING sum_assured::NUMERIC;
ALTER TABLE public.user_excel ALTER COLUMN premium TYPE NUMERIC(12,2) USING premium::NUMERIC;
ALTER TABLE public.user_excel
ALTER COLUMN mode TYPE VARCHAR(5) USING mode::VARCHAR;
