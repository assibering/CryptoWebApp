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

-- Commit all changes
COMMIT;
