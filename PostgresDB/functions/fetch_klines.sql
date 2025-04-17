CREATE OR REPLACE FUNCTION crypto.fetch_klines()
RETURNS void AS $$
DECLARE
    -- Timing variables
    start_time         TIMESTAMP;
    end_time           TIMESTAMP;
    fetch_start_time   BIGINT;
    fetch_end_time     BIGINT;
    current_epoch_time BIGINT;  -- Renamed from current_time

    -- Fetch control
    success            BOOLEAN := TRUE;
    last_fetch         BIGINT;

    -- API and data processing
    symbols            TEXT[] := ARRAY['DOGEUSDT', 'XRPUSDT', 'BNBUSDT', 'ETHUSDT', 'BTCUSDT', 'SOLUSDT'];
    symbol_name        TEXT;
    interval_param     TEXT := '30m';
    limit_param        INTEGER := 1000;
    api_url            TEXT;
    response           JSONB;
    kline              JSONB;
BEGIN
    -- Record function execution start time
    start_time := NOW();

    -- Get current time in milliseconds for Binance API
    current_epoch_time := (EXTRACT(EPOCH FROM NOW()) * 1000.0)::BIGINT;
    fetch_end_time := current_epoch_time;

    -- Get the last successful fetch time
    SELECT MAX(last_fetch_end_time) INTO last_fetch
    FROM crypto.fetch_jobs 
    WHERE job_name = 'klines_update' AND job_successful = TRUE;

    -- Set fetch_start_time if available
    IF last_fetch IS NOT NULL THEN
        fetch_start_time := last_fetch;
    END IF;

    -- Process each symbol
    FOREACH symbol_name IN ARRAY symbols LOOP
        BEGIN
            -- Construct API URL
            IF last_fetch IS NULL THEN
                api_url := format(
                    'https://api.binance.com/api/v3/klines?symbol=%s&interval=%s&limit=%s',
                    symbol_name, interval_param, limit_param
                );
            ELSE
                api_url := format(
                    'https://api.binance.com/api/v3/klines?symbol=%s&interval=%s&startTime=%s&endTime=%s&limit=%s',
                    symbol_name, interval_param, fetch_start_time, fetch_end_time, limit_param
                );
            END IF;

            -- Make HTTP request to Binance API
            SELECT content::jsonb INTO response
            FROM http_get(api_url);

            -- Loop through each kline in the response
            FOR kline IN SELECT jsonb_array_elements(response) LOOP
                INSERT INTO crypto.kline_assets (
                    symbol,
                    kline_open_time,
                    kline_close_time,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                    quote_asset_volume,
                    number_of_trades,
                    taker_buy_base_asset_volume,
                    taker_buy_quote_asset_volume
                ) VALUES (
                    symbol_name,
                    (TO_TIMESTAMP((kline->>0)::BIGINT / 1000)),
                    (TO_TIMESTAMP((kline->>6)::BIGINT / 1000)),
                    (kline->>1)::DECIMAL(18,8),
                    (kline->>2)::DECIMAL(18,8),
                    (kline->>3)::DECIMAL(18,8),
                    (kline->>4)::DECIMAL(18,8),
                    (kline->>5)::DECIMAL(18,8),
                    (kline->>7)::DECIMAL(18,8),
                    (kline->>8)::INTEGER,
                    (kline->>9)::DECIMAL(18,8),
                    (kline->>10)::DECIMAL(18,8)
                )
                ON CONFLICT (symbol, kline_open_time) DO UPDATE SET
                    kline_close_time              = EXCLUDED.kline_close_time,
                    open_price                   = EXCLUDED.open_price,
                    high_price                   = EXCLUDED.high_price,
                    low_price                    = EXCLUDED.low_price,
                    close_price                  = EXCLUDED.close_price,
                    volume                       = EXCLUDED.volume,
                    quote_asset_volume           = EXCLUDED.quote_asset_volume,
                    number_of_trades             = EXCLUDED.number_of_trades,
                    taker_buy_base_asset_volume  = EXCLUDED.taker_buy_base_asset_volume,
                    taker_buy_quote_asset_volume = EXCLUDED.taker_buy_quote_asset_volume;
            END LOOP;

        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Error fetching klines for %: %', symbol_name, SQLERRM;
            success := FALSE;
        END;
    END LOOP;

    -- Record function execution end time
    end_time := NOW();

    -- Log the fetch job
    INSERT INTO crypto.fetch_jobs (
        job_name,
        last_fetch_start_time,
        last_fetch_end_time,
        job_successful
    ) VALUES (
        'klines_update',
        0,  -- Simplified to avoid integer range issues
        fetch_end_time,
        success
    );

    -- Completion log
    RAISE NOTICE 'Kline fetch completed in % seconds. Success: %',
                 EXTRACT(EPOCH FROM (end_time - start_time)),
                 success;
END;
$$ LANGUAGE plpgsql;