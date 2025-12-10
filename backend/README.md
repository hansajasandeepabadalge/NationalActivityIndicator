# National Activity Indicator - Layer 2

Real-time indicator calculation system with ML classification, entity extraction, trend analysis, and REST API.

## Features

- **Rule-Based Classification**: Keyword-based indicator matching
- **ML Classification**: Logistic Regression/XGBoost with F1=0.926
- **Entity Extraction**: spaCy NER (6.7s for 200 articles)
- **Trend Analysis**: Multi-timeframe detection + forecasting
- **Narrative Generation**: Auto-generated explanations with emojis
- **REST API**: 7 endpoints for indicators, trends, anomalies
- **Dashboard**: Real-time visualization
- **Performance**: Redis caching, <2s response time

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start services
docker-compose up -d

# Run server
uvicorn app.main:app --reload

# Visit: http://localhost:8000
```

## API Endpoints

- `GET /api/v1/indicators` - List all indicators
- `GET /api/v1/indicators/{id}` - Indicator details
- `GET /api/v1/indicators/{id}/history` - Time series
- `GET /api/v1/indicators/trends` - Trend detection
- `GET /api/v1/indicators/anomalies` - Anomaly detection
- `GET /api/v1/indicators/alerts` - Recent alerts
- `GET /api/v1/indicators/composite` - Composite metrics
- `GET /health` - Health check
- `GET /docs` - API documentation

## Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/        # API endpoints
│   ├── layer2/
│   │   ├── data_ingestion/      # Article loading
│   │   ├── ml_classification/   # Rule-based + ML classifiers
│   │   ├── nlp_processing/      # Entity extraction
│   │   ├── indicator_calculation/ # Indicator calculators
│   │   ├── analysis/            # Trend detection, forecasting
│   │   └── narrative/           # Narrative generation
│   ├── db/                      # Database connections
│   ├── core/                    # Configuration
│   └── static/                  # Dashboard
├── data/                        # Historical data, mock articles
├── tests/                       # Unit + integration tests
└── scripts/                     # Pipelines
```

## Performance

- **ML F1 Score**: 0.926 (Hybrid), 0.759 (ML-only)
- **Entity Extraction**: ~30 articles/second
- **Trend Analysis**: 24 indicators × 90 days
- **API Response**: <2 seconds (cached)

## Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Day 2 Complete](DAY2_COMPLETE.md)
- [Day 3 Complete](DAY3_COMPLETE_WITH_ADAPTIVE_SCALING.md)
- [Day 4 Complete](DAY4_COMPLETE.md)
- [Day 5 Complete](DAY5_COMPLETE.md)
- [Day 6 Complete](DAY6_COMPLETE.md)
- [Day 7 Complete](DAY7_COMPLETE.md)

## Technology Stack

- **Backend**: FastAPI, Python 3.12
- **Databases**: TimescaleDB (PostgreSQL), MongoDB, Redis
- **ML/NLP**: scikit-learn, XGBoost, spaCy
- **Deployment**: Docker Compose

## Developer

Developer A - Layer 2 Implementation
