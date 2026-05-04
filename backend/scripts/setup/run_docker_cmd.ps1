param([string]$Command)
$BackendPath = "C:\Users\user\Desktop\National_Indicator\NationalActivityIndicator\backend"
docker run --rm --network backend_indicator_network -v "${BackendPath}:/app" -w /app python:3.12-slim sh -c $Command
