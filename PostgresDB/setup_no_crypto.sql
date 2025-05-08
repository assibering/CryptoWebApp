-- File: /opt/sql/setup_no_crypto.sql

\connect crypto_db;

-- 1. Setup schemas, tables
\i /opt/sql/init_tables_auth.sql

-- 2. Setup permissions
\i /opt/sql/authorised_services.sql