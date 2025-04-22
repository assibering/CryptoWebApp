-- First remove old jobs
SELECT cron.unschedule(jobid)
FROM cron.job
WHERE command LIKE 'DO $$DECLARE end_time BIGINT%';  -- safer filter

-- Then schedule one cron job every 30 minutes
SELECT cron.schedule('*/30 * * * *', 
$cron$
DO $$
DECLARE
    end_time BIGINT := (EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT;
    symbol TEXT;
    symbols TEXT[] := ARRAY['DOGEUSDT', 'XRPUSDT', 'BNBUSDT', 'ETHUSDT', 'BTCUSDT', 'SOLUSDT'];
    retry_attempt INT;
    retry_symbol TEXT;
BEGIN
    -- First fetch
    FOREACH symbol IN ARRAY symbols LOOP
        PERFORM crypto.fetch_klines(symbol, end_time);
    END LOOP;

    -- Then retry up to 3 times
    FOR retry_attempt IN 1..3 LOOP
        FOR retry_symbol IN
            SELECT DISTINCT f.symbol
            FROM crypto.fetch_jobs f
            WHERE f.job_successful = FALSE
            AND f.last_fetch_end_time = end_time
            AND NOT EXISTS (
                SELECT 1
                FROM crypto.fetch_jobs s
                WHERE s.symbol = f.symbol
                    AND s.last_fetch_end_time = end_time
                    AND s.job_successful = TRUE
            )
        LOOP
            RAISE NOTICE 'Retry attempt % for symbol %', retry_attempt, retry_symbol;
            PERFORM crypto.fetch_klines(retry_symbol, end_time);
        END LOOP;

        -- small sleep between retries to avoid hammering
        PERFORM pg_sleep(5); -- sleep 5 seconds if needed

    END LOOP;
END $$;
$cron$
);

-- Log
DO $$
BEGIN
    RAISE NOTICE 'Scheduled single cron job to fetch klines for all symbols every 30 minutes, using synchronized runtime NOW.';
END $$;