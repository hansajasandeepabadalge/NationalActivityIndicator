@echo off
REM Script to run Alembic migrations inside Docker container
REM This bypasses Windows host authentication issues

echo Running database migrations inside Docker container...
echo.

docker run --rm ^
  --network backend_indicator_network ^
  -v "%cd%\backend:/app" ^
  -w /app ^
  -e DATABASE_URL=postgresql://postgres:postgres_secure_2024@timescaledb:5432/national_indicator ^
  python:3.11-slim ^
  bash -c "pip install --quiet psycopg2-binary alembic sqlalchemy pydantic-settings && alembic upgrade head"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Migrations completed successfully!
) else (
    echo.
    echo ✗ Migration failed with error code %ERRORLEVEL%
    echo.
    echo Common issues:
    echo   - Docker network name might be different. Check with: docker network ls
    echo   - Backend path might be incorrect
    echo   - Database container might not be running
)
