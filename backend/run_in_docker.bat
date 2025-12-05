@echo off
REM Run Python scripts inside Docker container connected to TimescaleDB
echo Running script inside Docker container...
echo.

docker run --rm -it ^
  --network backend_indicator_network ^
  -v "%cd%:/app" ^
  -w /app ^
  -e DATABASE_URL=postgresql://postgres:postgres_secure_2024@national_indicator_timescaledb:5432/national_indicator ^
  -e MONGODB_URL=mongodb://admin:mongo_secure_2024@national_indicator_mongodb:27017/national_indicator?authSource=admin ^
  -e REDIS_URL=redis://national_indicator_redis:6379/0 ^
  python:3.12-slim sh -c "pip install -q -r requirements.txt && python %*"
