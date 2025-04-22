CREATE OR REPLACE FUNCTION crypto.fetch_klines(symbol_name TEXT, fetch_end_time BIGINT)
RETURNS void AS $$
DECLARE
    start_time           TIMESTAMP;
    end_time             TIMESTAMP;
    fetch_start_time     BIGINT;
    last_successful_fetch BIGINT;
    api_url              TEXT;
    response             JSONB;
    kline                JSONB;
    success              BOOLEAN := TRUE;
BEGIN
    start_time := NOW();

    -- Find last successful fetch for this symbol
    SELECT MAX(last_fetch_end_time) INTO last_successful_fetch
    FROM crypto.fetch_jobs
    WHERE symbol = symbol_name AND job_successful = TRUE;

    IF last_successful_fetch IS NOT NULL THEN
        fetch_start_time := last_successful_fetch;
    ELSE
        fetch_start_time := NULL; -- First ever fetch for this symbol
    END IF;

    -- Construct API URL
    IF fetch_start_time IS NULL THEN
        -- First time: no startTime, but we must use endTime to align across symbols
        api_url := format(
            'https://api.binance.com/api/v3/klines?symbol=%s&interval=30m&endTime=%s&limit=1000',
            symbol_name, fetch_end_time
        );
    ELSE
        -- Normal case: both startTime and endTime
        api_url := format(
            'https://api.binance.com/api/v3/klines?symbol=%s&interval=30m&startTime=%s&endTime=%s&limit=1000',
            symbol_name, fetch_start_time, fetch_end_time
        );
    END IF;

    -- Make API call
    BEGIN
        SELECT content::jsonb INTO response
        FROM http_get(api_url);

        -- Insert klines
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
        RAISE NOTICE 'Error fetching klines for symbol %: %', symbol_name, SQLERRM;
        success := FALSE;
    END;

    -- Log the fetch attempt
    INSERT INTO crypto.fetch_jobs (
        symbol,
        last_fetch_start_time,
        last_fetch_end_time,
        job_successful,
        created_at
    ) VALUES (
        symbol_name,
        COALESCE(fetch_start_time, 0),
        fetch_end_time,
        success,
        NOW()
    );

    end_time := NOW();
    RAISE NOTICE 'Kline fetch for % completed in % seconds. Success: %',
                 symbol_name,
                 EXTRACT(EPOCH FROM (end_time - start_time)),
                 success;

END;
$$ LANGUAGE plpgsql;
