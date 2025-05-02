-- Create the schema if not exists
CREATE SCHEMA IF NOT EXISTS auth;

-- Create the users table
CREATE TABLE IF NOT EXISTS auth.users (
    email VARCHAR(50) PRIMARY KEY,
    hashed_password VARCHAR(200), -- hashed (including salt)
    is_active BOOLEAN
);

-- create the users outbox table
CREATE TABLE IF NOT EXISTS auth.users_outbox (
    id UUID PRIMARY KEY,
    aggregatetype TEXT NOT NULL,
    aggregateid TEXT NOT NULL,
    type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at BIGINT NOT NULL,
    transaction_id TEXT
);

-- Create the subscriptions table
CREATE TABLE IF NOT EXISTS auth.subscriptions (
    subscription_id UUID PRIMARY KEY,
    subscription_type VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL
);

-- create the subscriptions outbox table
CREATE TABLE IF NOT EXISTS auth.subscriptions_outbox (
    id UUID PRIMARY KEY,
    aggregatetype TEXT NOT NULL,
    aggregateid TEXT NOT NULL,
    type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at BIGINT NOT NULL,
    transaction_id TEXT
);
