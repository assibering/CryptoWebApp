-- init_tables.sql

-- Create the schema if not exists
CREATE SCHEMA IF NOT EXISTS crypto;

-- Create the kline_assets table
CREATE TABLE IF NOT EXISTS crypto.kline_assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL, -- e.g. BTCUSDT, Bitcoin is base, USDT is quote
    kline_open_time TIMESTAMPTZ NOT NULL, -- [kline_open_time, kline_close_time] is the interval for which OHLC is stored in UTC timezone internally
    kline_close_time TIMESTAMPTZ NOT NULL,
    open_price DECIMAL(18, 8) NOT NULL, -- This and the 3 following is OHLC, used to build kline
    high_price DECIMAL(18, 8) NOT NULL,
    low_price DECIMAL(18, 8) NOT NULL,
    close_price DECIMAL(18, 8) NOT NULL,
    volume DECIMAL(18, 8), -- amount of BTC traded
    quote_asset_volume DECIMAL(18, 8), -- amount of USD traded
    number_of_trades INTEGER, -- number of trades completed
    taker_buy_base_asset_volume DECIMAL(18,8), -- BTC bought by 'takers' using market orders
    taker_buy_quote_asset_volume DECIMAL(18,8), -- USD spent by the above 'takers'
    CONSTRAINT kline_assets_symbol_open_time_unique UNIQUE(symbol, kline_open_time) -- ensure that there are no duplicates
);

-- -- Create the options table
-- CREATE TABLE IF NOT EXISTS crypto.options (
--     id SERIAL PRIMARY KEY,
--     expiryDate BIGINT NOT NULL, -- Date option expires, i.e. when the option can be exercised
--     symbol VARCHAR(40) NOT NULL, -- e.g. "BTC-250627-125000-P" <crypto> - <expiration> - <strike price> - <(C)all or (P)ut>
--     side CHAR(4) NOT NULL, -- CALL or PUT
--     strikePrice DECIMAL(18,8) NOT NULL, -- price in quote, e.g. USDT, that buyer is buying the right to sell the underlying asset for
--     underlying VARCHAR(20) NOT NULL, -- e.g. BTCUSDT, Bitcoin is base, USDT is quote
--     unit DECIMAL(18,8) NOT NULL, -- e.g. 10 means that 1 contract controls 10 Bitcoins
--     makerFeeRate DECIMAL(18,8) NOT NULL, -- if you place a limit order (tell the market you are willing to buy/market maker), you pay premium * makerFeeRate
--     takerFeeRate DECIMAL(18,8) NOT NULL, -- if you place a market order (buy an existing opportunity/market taker), you pay premium * takerFeeRate
--     minQty DECIMAL(18,8) NOT NULL, -- min number of BTC you can control, Final Premium = Qty * Premium/MarkPrice
--     maxQty DECIMAL(18,8) NOT NULL, -- max number of BTC you can control, Final Premium = Qty * Premium/MarkPrice
--     stepSize DECIMAL(18,8) NOT NULL, -- Qty must be divisible by the stepSize, i.e. Qty % stepSize = 0.
--     initialMargin DECIMAL(18,8) NOT NULL, -- Sellers must have X% * strikePrice * Qty * Unit Size to open position
--     maintenanceMargin DECIMAL(18,8) NOT NULL, -- Sellers must maintain an account value of X% * strikePrice or risk liquidation
--     minInitialMargin DECIMAL(18,8) NOT NULL, -- Sellers must have X% * strikePrice minimum to open position
--     minMaintenanceMargin DECIMAL(18,8) NOT NULL, -- Sellers must maintain an account value of X% * strikePrice or automatic liquidation
--     priceScale Integer NOT NULL, -- Premiums are allowed X decimals, e.g. premium = 21000.0
--     quantityScale Integer NOT NULL, -- Quantities can have 2 decimals, e.g. I can control 0.01 BTC
--     quoteAsset VARCHAR(10) NOT NULL, -- Currency I use to buy the option, e.g. USDT
--     minPrice DECIMAL(18,8) NOT NULL, -- min price of premium
--     maxPrice DECIMAL(18,8) NOT NULL, -- max price of premium
--     tickSize DECIMAL(18,8) NOT NULL -- premium must be divisible by tickSize, i.e. premium % tickSize = 0
-- );

-- Create the fetch_jobs table
CREATE TABLE IF NOT EXISTS crypto.fetch_jobs (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    last_fetch_start_time BIGINT NOT NULL DEFAULT 0,
    last_fetch_end_time BIGINT NOT NULL,
    job_successful BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);


-- Create the schema if not exists
CREATE SCHEMA IF NOT EXISTS auth;

-- Create the users table
CREATE TABLE IF NOT EXISTS auth.users (
    email VARCHAR(50) PRIMARY KEY,
    hashed_password VARCHAR(200), -- hashed (including salt)
    is_active BOOLEAN
);
