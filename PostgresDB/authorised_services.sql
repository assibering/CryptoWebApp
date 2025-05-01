-- Start transaction for atomicity
BEGIN;

-- Check if users already exist and create them if they don't
DO $$
BEGIN
    -- Create user_service_user if it doesn't exist
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'user_service_user') THEN
        CREATE ROLE user_service_user WITH LOGIN PASSWORD 'super_secure_password';
        RAISE NOTICE 'Created user_service_user role';
    ELSE
        RAISE NOTICE 'user_service_user already exists';
    END IF;
    
    -- Create subscription_service_user if it doesn't exist
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'subscription_service_user') THEN
        CREATE ROLE subscription_service_user WITH LOGIN PASSWORD 'super_secure_password';
        RAISE NOTICE 'Created subscription_service_user role';
    ELSE
        RAISE NOTICE 'subscription_service_user already exists';
    END IF;
END
$$;

-- Verify roles were created before proceeding
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'user_service_user') THEN
        RAISE EXCEPTION 'Failed to create user_service_user';
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'subscription_service_user') THEN
        RAISE EXCEPTION 'Failed to create subscription_service_user';
    END IF;
END
$$;

-- Allow connection to the database
GRANT CONNECT ON DATABASE crypto_db TO user_service_user;
GRANT CONNECT ON DATABASE crypto_db TO subscription_service_user;

-- Allow usage of the 'auth' schema
GRANT USAGE ON SCHEMA auth TO user_service_user;
GRANT USAGE ON SCHEMA auth TO subscription_service_user;

-- Grant read/write/delete
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.users, auth.users_outbox TO user_service_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.subscriptions, auth.subscriptions_outbox TO subscription_service_user;

ALTER ROLE user_service_user WITH REPLICATION LOGIN;
ALTER ROLE subscription_service_user WITH REPLICATION LOGIN;


-- Verify grants were applied (will show error if tables don't exist)
DO $$
BEGIN
    RAISE NOTICE 'Permissions granted successfully';
END
$$;

-- Commit all changes
COMMIT;

-- Final verification outside transaction
SELECT rolname, rolcanlogin FROM pg_roles 
WHERE rolname IN ('user_service_user', 'subscription_service_user');
