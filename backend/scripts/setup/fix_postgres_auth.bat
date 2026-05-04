@echo off
echo Fixing PostgreSQL authentication...
echo.

REM Step 1: Backup original pg_hba.conf
docker exec national_indicator_timescaledb cp /var/lib/postgresql/data/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf.bak

REM Step 2: Create new pg_hba.conf with proper rules
docker exec national_indicator_timescaledb sh -c "cat > /var/lib/postgresql/data/pg_hba.conf << 'EOF'
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections (Unix socket)
local   all             all                                     trust

# IPv4 local connections - TRUST for development
host    all             all             127.0.0.1/32            trust
host    all             all             172.16.0.0/12           trust
host    all             all             192.168.0.0/16          trust

# IPv6 local connections
host    all             all             ::1/128                 trust

# Docker network connections
host    all             all             all                     md5

# Replication
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
EOF"

REM Step 3: Restart PostgreSQL to apply changes
echo Restarting PostgreSQL container...
docker restart national_indicator_timescaledb

REM Step 4: Wait for PostgreSQL to be ready
echo Waiting for PostgreSQL to start...
timeout /t 5 /nobreak >nul 2>&1

REM Step 5: Test connection
echo.
echo Testing connection...
python test_db_connection.py

echo.
echo Done!
pause
