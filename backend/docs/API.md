# API Documentation

## Base URL
`http://localhost:8000/api/v1`

## Endpoints

### 1. List Indicators
`GET /indicators`

Returns list of all available indicators.

### 2. Indicator Details
`GET /indicators/{id}`

Get detailed information for specific indicator.

### 3. Historical Data
`GET /indicators/{id}/history?days=30`

Get time series data for indicator.

### 4. Trends
`GET /indicators/trends/?min_strength=0.5`

Get indicators with strong trends.

### 5. Anomalies
`GET /indicators/anomalies/?threshold=2.0`

Detect anomalies in indicator values.

### 6. Alerts
`GET /indicators/alerts/?hours=24`

Get recent alerts for significant changes.

### 7. Composite Metrics
`GET /indicators/composite/`

Get composite indicators (economic health, stability).

## Example

```bash
curl http://localhost:8000/api/v1/indicators
```
