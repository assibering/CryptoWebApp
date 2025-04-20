-- Connect to your database (psql client or Adminer, DBeaver etc.)
CREATE ROLE user_service_user WITH LOGIN PASSWORD 'super_secure_password';

-- Allow connection to the database
GRANT CONNECT ON DATABASE crypto_db TO user_service_user;

-- Allow usage of the 'auth' schema
GRANT USAGE ON SCHEMA auth TO user_service_user;

-- Grant read/write/delete on 'auth.user' table only
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE auth.users TO user_service_user;
