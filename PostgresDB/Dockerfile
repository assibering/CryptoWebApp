###########################################
# BUILDER stage
###########################################
FROM postgres:17 AS builder

# Install required packages, including libcurl for pgsql-http
RUN apt-get update && apt-get install -y \
    postgresql-contrib \
    postgresql-server-dev-17 \
    build-essential \
    git \
    libcurl4-openssl-dev \
    && git clone https://github.com/pramsey/pgsql-http.git /pgsql-http \
    && cd /pgsql-http && make && make install \
    && git clone https://github.com/citusdata/pg_cron.git /pg_cron \
    && cd /pg_cron && make && make install \
    && rm -rf /var/lib/apt/lists/*

###########################################
# WITHOUT CRYPTO FETCH SETUP stage
###########################################

FROM postgres:17 AS no-crypto-fetch-setup

# Install runtime dependencies
# pgsql-http needs libcurl at runtime to make HTTP requests
RUN apt-get update && apt-get install -y \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

# Create directories for SQL files
RUN mkdir -p /opt/sql/functions /opt/sql/schedules && \
    chown -R postgres:postgres /opt/sql

# Copy SQL files to the container
# Files in /docker-entrypoint-initdb.d/ are automatically executed by postgres on container start if the database is empty
# The order of execution is dictated by the naming, 00 first, 01 after, and so on.
# In this case we execute init_db.sql first and then we execute setup.sql
COPY --chown=postgres:postgres init_db.sql /docker-entrypoint-initdb.d/00_init_db.sql
COPY --chown=postgres:postgres setup_no_crypto.sql /docker-entrypoint-initdb.d/01_setup_no_crypto.sql
COPY --chown=postgres:postgres init_tables.sql /opt/sql/
COPY --chown=postgres:postgres authorised_services.sql /opt/sql/
COPY --chown=postgres:postgres functions/ /opt/sql/functions/
COPY --chown=postgres:postgres schedules/ /opt/sql/schedules/

# Copy built extensions from builder stage
COPY --from=builder /usr/lib/postgresql /usr/lib/postgresql
COPY --from=builder /usr/share/postgresql /usr/share/postgresql

# Copy custom postgresql.conf
COPY postgresql.conf /etc/postgresql/postgresql.conf

# Set proper permissions for the entrypoint directory
RUN chown -R postgres:postgres /docker-entrypoint-initdb.d/

# Switch to postgres user for any commands run at build time after this point
USER postgres

# Start Postgres with custom config file
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]

###########################################
# FULL SETUP stage
###########################################
FROM postgres:17 AS full-setup

# Install runtime dependencies
# pgsql-http needs libcurl at runtime to make HTTP requests
RUN apt-get update && apt-get install -y \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

# Create directories for SQL files
RUN mkdir -p /opt/sql/functions /opt/sql/schedules && \
    chown -R postgres:postgres /opt/sql

# Copy SQL files to the container
# Files in /docker-entrypoint-initdb.d/ are automatically executed by postgres on container start if the database is empty
# The order of execution is dictated by the naming, 00 first, 01 after, and so on.
# In this case we execute init_db.sql first and then we execute setup.sql
COPY --chown=postgres:postgres init_db.sql /docker-entrypoint-initdb.d/00_init_db.sql
COPY --chown=postgres:postgres setup.sql /docker-entrypoint-initdb.d/01_setup.sql
COPY --chown=postgres:postgres init_tables.sql /opt/sql/
COPY --chown=postgres:postgres authorised_services.sql /opt/sql/
COPY --chown=postgres:postgres functions/ /opt/sql/functions/
COPY --chown=postgres:postgres schedules/ /opt/sql/schedules/

# Copy built extensions from builder stage
COPY --from=builder /usr/lib/postgresql /usr/lib/postgresql
COPY --from=builder /usr/share/postgresql /usr/share/postgresql

# Copy custom postgresql.conf
COPY postgresql.conf /etc/postgresql/postgresql.conf

# Set proper permissions for the entrypoint directory
RUN chown -R postgres:postgres /docker-entrypoint-initdb.d/

# Switch to postgres user for any commands run at build time after this point
USER postgres

# Start Postgres with custom config file
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]