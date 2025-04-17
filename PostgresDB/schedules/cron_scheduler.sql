-- Setup pg_cron jobs to schedule the kline fetch function

-- Schedule the kline fetch function to run every 30 minutes
-- First remove existing job if it exists
SELECT cron.unschedule(jobid) 
FROM cron.job 
WHERE command = 'SELECT crypto.fetch_klines()';

-- Then create the new schedule
SELECT cron.schedule('*/30 * * * *', 'SELECT crypto.fetch_klines()');

-- Log that the schedule has been set up
DO $$
BEGIN
    RAISE NOTICE 'Scheduled crypto.fetch_klines() to run every 30 minutes';
END $$;