-- Master script to set up everything in the correct order
-- To run after initialisation of database

-- Switch into the crypto_db database
\connect crypto_db;

-- Create the http extension here, now that the DB exists
CREATE EXTENSION IF NOT EXISTS http;
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 1. run init to create schemas and tables
\i /opt/sql/init_tables.sql

-- 2. Create the fetch_klines function
\i /opt/sql/functions/fetch_klines.sql

-- 3. Set up the cron job
\i /opt/sql/schedules/cron_scheduler.sql

-- 4. Run the function once immediately to initialize data
SELECT crypto.fetch_klines();

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Setup completed successfully. The fetch_klines function will run every 30 minutes.';
END $$;