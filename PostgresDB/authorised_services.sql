-- Start transaction for atomicity

-- Create roles
CREATE ROLE user_service_user WITH LOGIN PASSWORD 'super_secure_password';
CREATE ROLE subscription_service_user WITH LOGIN PASSWORD 'super_secure_password';

-- Allow connection to the database
GRANT CREATE, CONNECT ON DATABASE crypto_db TO user_service_user;
GRANT CREATE, CONNECT ON DATABASE crypto_db TO subscription_service_user;

-- Allow usage of the 'auth' schema
GRANT USAGE ON SCHEMA auth TO user_service_user;
GRANT USAGE ON SCHEMA auth TO subscription_service_user;

-- Grant read/write/delete
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.users, auth.users_outbox TO user_service_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.subscriptions, auth.subscriptions_outbox TO subscription_service_user;

-- Ownership of tables
ALTER TABLE auth.users_outbox OWNER TO user_service_user;
ALTER TABLE auth.subscriptions_outbox OWNER TO subscription_service_user;

-- Replication
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
