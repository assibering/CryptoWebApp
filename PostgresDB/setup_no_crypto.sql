-- File: /opt/sql/setup_no_crypto.sql

\connect crypto_db;

CREATE EXTENSION IF NOT EXISTS http;
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 1. Setup schemas, tables
\i /opt/sql/init_tables.sql

-- 2. Setup permissions
\i /opt/sql/authorised_services.sql