"""
Permanent fix for PostgreSQL authentication issues on Windows-Docker
This script configures pg_hba.conf to use MD5 instead of SCRAM-SHA-256
"""

import subprocess
import time

def fix_postgres_auth():
    """Fix PostgreSQL authentication configuration"""

    print("=" * 60)
    print("PostgreSQL Windows-Docker Authentication Fix")
    print("=" * 60)

    # Step 1: Update pg_hba.conf inside container
    print("\n1. Updating pg_hba.conf to use MD5 authentication...")

    pg_hba_config = """# PostgreSQL Client Authentication Configuration
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
"""

    # Write config to container
    cmd = f'''docker exec national_indicator_timescaledb sh -c "cat > /var/lib/postgresql/data/pg_hba.conf <<'EOF'
{pg_hba_config}
EOF"'''

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ pg_hba.conf updated successfully")
    else:
        print(f"   ❌ Failed to update pg_hba.conf: {result.stderr}")
        return False

    # Step 2: Set password to MD5 hash
    print("\n2. Setting PostgreSQL password...")
    cmd = "docker exec national_indicator_timescaledb psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'postgres_secure_2024';\""

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Password set successfully")
    else:
        print(f"   ❌ Failed to set password: {result.stderr}")
        return False

    # Step 3: Reload PostgreSQL configuration
    print("\n3. Reloading PostgreSQL configuration...")
    cmd = "docker exec national_indicator_timescaledb psql -U postgres -c \"SELECT pg_reload_conf();\""

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Configuration reloaded")
    else:
        print(f"   ❌ Failed to reload: {result.stderr}")
        return False

    # Step 4: Test connection
    print("\n4. Testing connection...")
    time.sleep(2)  # Give PostgreSQL time to reload

    try:
        import psycopg2
        conn = psycopg2.connect(
            "postgresql://postgres:postgres_secure_2024@127.0.0.1:5432/national_indicator"
        )
        conn.close()
        print("   ✅ Connection test SUCCESSFUL!")
        print("\n" + "=" * 60)
        print("✅ PostgreSQL authentication PERMANENTLY FIXED!")
        print("=" * 60)
        print("\nYou can now connect using:")
        print("  postgresql://postgres:postgres_secure_2024@127.0.0.1:5432/national_indicator")
        return True
    except Exception as e:
        print(f"   ❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_postgres_auth()
    exit(0 if success else 1)
