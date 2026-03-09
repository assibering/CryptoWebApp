-- Start transaction for atomicity
BEGIN;

-- =========================
-- Schema usage grants
-- =========================
GRANT USAGE ON SCHEMA auth TO user_service_user;
GRANT USAGE ON SCHEMA auth TO subscription_service_user;
GRANT USAGE ON SCHEMA auth TO debezium_user;

-- Optional: allow service users to create tables in schema (for testing / migrations)
GRANT CREATE ON SCHEMA auth TO user_service_user;
GRANT CREATE ON SCHEMA auth TO subscription_service_user;

-- =========================
-- Explicit privileges on existing tables
-- =========================
-- user_service_user
GRANT SELECT, INSERT, UPDATE, DELETE 
    ON TABLE auth.users, auth.users_outbox 
    TO user_service_user;

GRANT USAGE, SELECT 
    ON ALL SEQUENCES IN SCHEMA auth 
    TO user_service_user;

-- subscription_service_user
GRANT SELECT, INSERT, UPDATE, DELETE 
    ON TABLE auth.subscriptions, auth.subscriptions_outbox 
    TO subscription_service_user;

GRANT USAGE, SELECT 
    ON ALL SEQUENCES IN SCHEMA auth 
    TO subscription_service_user;

-- debezium_user (CDC / replication)
GRANT SELECT 
    ON TABLE auth.users_outbox, auth.subscriptions_outbox 
    TO debezium_user;

-- =========================
-- Default privileges for future tables and sequences
-- =========================
-- Any new tables created in auth schema will automatically grant these privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA auth
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO user_service_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth
GRANT USAGE, SELECT ON SEQUENCES TO user_service_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO subscription_service_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth
GRANT USAGE, SELECT ON SEQUENCES TO subscription_service_user;

-- =========================
-- Pre-create publication for Debezium (execute as superuser)
-- =========================
CREATE PUBLICATION dbz_publication_user FOR TABLE auth.users_outbox;
CREATE PUBLICATION dbz_publication_subscription FOR TABLE auth.subscriptions_outbox;

-- =========================
-- Verification / notice
-- =========================
DO $$
BEGIN
    RAISE NOTICE 'Permissions granted successfully';
END
$$;

-- Commit all changes
COMMIT;

-- Final verification outside transaction
SELECT rolname, rolcanlogin 
FROM pg_roles 
WHERE rolname IN ('user_service_user', 'subscription_service_user', 'debezium_user');