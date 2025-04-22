-- File: /opt/sql/setup.sql

\connect crypto_db;

CREATE EXTENSION IF NOT EXISTS http;
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 1. Setup schemas, tables
\i /opt/sql/init_tables.sql

-- 2. Setup permissions
\i /opt/sql/authorised_services.sql

-- 3. Create the fetch function
\i /opt/sql/functions/fetch_klines.sql

-- 4. Setup the cron jobs
\i /opt/sql/schedules/cron_scheduler.sql

-- 5. Initial per-symbol fetch with retries
DO $$
DECLARE
    fetch_now BIGINT := (EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT;
    symbol TEXT;
    symbols TEXT[] := ARRAY['DOGEUSDT', 'XRPUSDT', 'BNBUSDT', 'ETHUSDT', 'BTCUSDT', 'SOLUSDT'];
BEGIN
    FOREACH symbol IN ARRAY symbols LOOP
        PERFORM crypto.fetch_klines(symbol, fetch_now);
    END LOOP;
END $$;

-- 6. Retry failures up to 3 times
DO $$
DECLARE
    retry_attempt INT;
    retry_symbol TEXT;
    retry_end_time BIGINT;
BEGIN
    FOR retry_attempt IN 1..3 LOOP
        FOR retry_symbol, retry_end_time IN
            SELECT symbol, last_fetch_end_time
            FROM (
                SELECT DISTINCT ON (symbol) symbol, last_fetch_end_time, job_successful
                FROM crypto.fetch_jobs
                ORDER BY symbol, created_at DESC
            ) latest_attempts
            WHERE job_successful = FALSE
            AND NOT EXISTS (
                SELECT 1
                FROM crypto.fetch_jobs s
                WHERE s.symbol = latest_attempts.symbol
                    AND s.last_fetch_end_time = latest_attempts.last_fetch_end_time
                    AND s.job_successful = TRUE
            )
        LOOP
            RAISE NOTICE 'Retry attempt % for symbol %', retry_attempt, retry_symbol;
            PERFORM crypto.fetch_klines(retry_symbol, retry_end_time);
        END LOOP;

        -- small sleep between retries to avoid hammering
        PERFORM pg_sleep(5); -- sleep 5 seconds if needed
        
    END LOOP;
END $$;

