-- Start transaction for atomicity
BEGIN;

-- Create roles
CREATE ROLE user_service_user WITH LOGIN PASSWORD 'super_secure_password';
CREATE ROLE subscription_service_user WITH LOGIN PASSWORD 'super_secure_password';
CREATE ROLE debezium_user WITH REPLICATION LOGIN PASSWORD 'secure_debezium_password';

-- Allow connection to the database
GRANT CONNECT ON DATABASE crypto_db TO user_service_user;
GRANT CONNECT ON DATABASE crypto_db TO subscription_service_user;
GRANT CONNECT ON DATABASE crypto_db TO debezium_user;

-- Allow usage of the 'auth' schema
GRANT USAGE ON SCHEMA auth TO user_service_user;
GRANT USAGE ON SCHEMA auth TO subscription_service_user;
GRANT USAGE ON SCHEMA auth TO debezium_user;

-- Grant privileges to user_service_user
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.users TO user_service_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.users_outbox TO user_service_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA auth TO user_service_user;

-- Grant privileges to subscription_service_user
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.subscriptions TO subscription_service_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.subscriptions_outbox TO subscription_service_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA auth TO subscription_service_user;

-- Grant CREATE on schema for testing purposes (table creation/deletion)
GRANT CREATE ON SCHEMA auth TO user_service_user;
GRANT CREATE ON SCHEMA auth TO subscription_service_user;

-- Pre-create publication for Debezium (execute as superuser)
CREATE PUBLICATION dbz_publication_user FOR TABLE auth.users_outbox;
CREATE PUBLICATION dbz_publication_subscription FOR TABLE auth.subscriptions_outbox;

-- Grant debezium_user minimal privileges needed for CDC
GRANT SELECT ON TABLE auth.users_outbox TO debezium_user;
GRANT SELECT ON TABLE auth.subscriptions_outbox TO debezium_user;

-- Verify grants were applied
DO $$
BEGIN
    RAISE NOTICE 'Permissions granted successfully';
END
$$;

-- Commit all changes
COMMIT;

-- Final verification outside transaction
SELECT rolname, rolcanlogin FROM pg_roles 
WHERE rolname IN ('user_service_user', 'subscription_service_user', 'debezium_user');
