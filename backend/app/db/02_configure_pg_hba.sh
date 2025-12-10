#!/bin/bash
# Configure pg_hba.conf for Windows-Docker compatibility
# This script runs during PostgreSQL initialization

set -e

echo "Configuring pg_hba.conf for Windows-Docker compatibility..."

# Copy custom pg_hba.conf
cat > /var/lib/postgresql/data/pg_hba.conf <<'EOF'
# PostgreSQL Client Authentication Configuration
# Custom configuration for Windows-Docker compatibility

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections (localhost)
host    all             all             127.0.0.1/32            md5

# IPv6 local connections
host    all             all             ::1/128                 md5

# Docker bridge network
host    all             all             172.16.0.0/12           md5
host    all             all             172.17.0.0/16           md5

# Allow all other connections with MD5
host    all             all             0.0.0.0/0               md5

# Replication connections
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                 md5
EOF

echo "✅ pg_hba.conf configured successfully"
