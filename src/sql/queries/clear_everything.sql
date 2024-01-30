DO $$ 
DECLARE 
    sql_stmt TEXT; 
BEGIN
    SELECT 
        string_agg('DROP TABLE IF EXISTS "' || tablename || '" CASCADE;', ' ') 
    INTO 
        sql_stmt 
    FROM 
        pg_tables
    WHERE 
        schemaname = 'public'; 
    EXECUTE sql_stmt; 
END $$;