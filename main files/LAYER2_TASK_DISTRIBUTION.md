# Layer 2 Task Distribution Guide
## 7-Day Development Plan for 2 Developers (Remote Work)

---

## 📋 QUICK REFERENCE

**Timeline**: 7 days (1 week)
**Team**: 2 ML/NLP experienced developers working remotely
**Goal**: Build complete Layer 2 with Iteration 1 + 2 (including ML classification)

### Developer Roles

| Developer | Primary Focus | Days |
|-----------|--------------|------|
| **Developer A (You)** | Data Processing, ML Classification, Entity Extraction, Trends | Days 2-5 |
| **Developer B (Team Member)** | Databases, Indicators, Sentiment, Anomaly Detection | Days 2-5 |
| **Both Together** | Foundation (Day 1), Integration (Days 6-7) | Days 1, 6-7 |

---

## 🗓️ DAY-BY-DAY TASK BREAKDOWN

---

## DAY 1: FOUNDATION (Both Developers Together - 8 hours)

### Why Together?
Setting up the foundation together ensures both developers have:
- Same database environment
- Consistent project structure
- Shared mock data to work with independently
- Clear integration contracts

### Morning Tasks (Both - 4 hours)

#### ✅ Task 1.1: Docker Compose Setup (90 mins)
**File**: `docker-compose.yml`

```yaml
services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: national_indicator
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"

volumes:
  postgres_data:
  mongo_data:
```

**Commands to run**:
```bash
cd backend
docker-compose up -d
docker-compose ps  # Verify all containers running
```

#### ✅ Task 1.2: Environment Configuration (30 mins)
**Files**: `backend/.env.example`, `backend/.env`

```env
# Database URLs
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/national_indicator
TIMESCALEDB_URL=postgresql://postgres:postgres@localhost:5432/national_indicator
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379

# Project Settings
PROJECT_NAME=National Activity Indicator
API_V1_STR=/api/v1
```

**Update**: `backend/app/core/config.py`

#### ✅ Task 1.3: Database Schemas (2 hours)
**Files to create**:

1. `backend/app/db/init_timescale.sql` - TimescaleDB setup
2. `backend/alembic/versions/001_initial_layer2_schema.py` - Migration script
3. `backend/app/models/indicator.py` - Indicator definition models
4. `backend/app/models/indicator_value.py` - Time-series models
5. `backend/app/models/article_mapping.py` - Article-indicator mappings

**Tables to create**:
- `indicator_definitions`
- `indicator_keywords`
- `indicator_dependencies`
- `indicator_thresholds`
- `article_indicator_mappings`
- `indicator_values` (hypertable)
- `indicator_events` (hypertable)
- `indicator_trends` (hypertable)

**Run migrations**:
```bash
cd backend
alembic upgrade head
```

### Afternoon Tasks (Both - 4 hours)

#### ✅ Task 1.4: Project Structure Creation (30 mins)
Create the complete `backend/app/layer2/` directory structure:

```
backend/app/layer2/
├── __init__.py
├── data_ingestion/
│   ├── __init__.py
│   ├── article_fetcher.py
│   ├── mock_data_generator.py
│   └── validator.py
├── classification/
│   ├── __init__.py
│   ├── rule_based.py
│   ├── ml_classifier.py
│   └── hybrid.py
├── nlp/
│   ├── __init__.py
│   ├── sentiment_analyzer.py
│   └── entity_extractor.py
├── indicators/
│   ├── __init__.py
│   ├── calculator.py
│   ├── weighting.py
│   ├── composite_calculator.py
│   └── registry.py
├── analysis/
│   ├── __init__.py
│   ├── trend_detector.py
│   ├── anomaly_detector.py
│   ├── forecaster.py
│   └── dependency_mapper.py
├── narrative/
│   ├── __init__.py
│   └── generator.py
├── storage/
│   ├── __init__.py
│   └── calculation_storage.py
├── alerting/
│   ├── __init__.py
│   ├── alert_manager.py
│   └── event_logger.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

#### ✅ Task 1.5: Dependencies Installation (30 mins)
**File**: `backend/requirements.txt`

Add these dependencies:
```txt
# Existing
fastapi
uvicorn
pydantic-settings

# Database
sqlalchemy==2.0.23
psycopg2-binary
pymongo
redis
alembic

# ML & NLP
scikit-learn
xgboost
transformers
torch
sentence-transformers
spacy
nltk

# Data Processing
pandas
numpy
scipy

# Time Series
prophet
statsmodels

# Utilities
python-dateutil
pyyaml
python-multipart
```

**Install**:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### ✅ Task 1.6: Mock Data Generation (2.5 hours)
**This is CRITICAL** - Both developers need the same mock data to work independently.

**Files to create**:
- `backend/app/layer2/data_ingestion/mock_data_generator.py` (generator script)
- `backend/mock_data/articles_political.json` (50 articles)
- `backend/mock_data/articles_economic.json` (50 articles)
- `backend/mock_data/articles_social.json` (50 articles)
- `backend/mock_data/articles_environmental.json` (30 articles)
- `backend/mock_data/articles_mixed.json` (20 articles)

**Mock Article Schema** (AGREED CONTRACT):
```python
{
    "article_id": "pol_001",  # Unique ID
    "content": {
        "title": "Transport workers announce nationwide strike",
        "body": "Full article text here...",
        "summary": "Brief summary (optional)"
    },
    "metadata": {
        "source": "Daily Mirror",
        "source_credibility": 0.85,  # 0.0-1.0
        "publish_timestamp": "2025-11-28T14:30:00Z",
        "language_original": "en"
    },
    "initial_classification": {
        "keywords": ["strike", "transport", "workers"],
        "detected_language": "en"
    },
    "quality": {
        "credibility_score": 0.85,
        "word_count": 156,
        "is_duplicate": false
    }
}
```

**Generate at least**:
- 50 political articles (protests, strikes, government)
- 50 economic articles (inflation, currency, business)
- 50 social articles (public sentiment, cost of living)
- 30 environmental articles (weather, floods, disasters)
- 20 mixed articles (multiple categories)

**Total**: 200+ articles

#### ✅ Task 1.7: Integration Test (30 mins)
**File**: `backend/scripts/test_day1_setup.py`

Test that:
- All databases are accessible
- Can create and query tables
- Mock data loads correctly
- Both developers can run the same test successfully

### Day 1 End Checkpoint ✅
- [ ] Docker containers running (postgres, mongodb, redis)
- [ ] Database schemas created in PostgreSQL
- [ ] TimescaleDB extension enabled
- [ ] Project structure complete
- [ ] All dependencies installed
- [ ] 200+ mock articles generated
- [ ] Both developers can connect to all databases
- [ ] Mock data loads successfully

**Git**: Merge to `main`, tag as `v0.1-infrastructure`

---

## DAY 2-5: PARALLEL DEVELOPMENT

### 🚨 IMPORTANT: Daily Communication
- **Morning Standup** (9 AM, 15 mins): What you did, what you're doing, blockers
- **End of Day Sync** (6 PM, 15 mins): Progress update, integration check
- **Shared Documentation**: Update a shared Google Doc/Notion with progress

---

## DAY 2: CORE PIPELINES

---

## 👤 DEVELOPER A TASKS (Day 2)

### Your Focus: Data Processing & Classification Pipeline

#### ✅ Task A2.1: Article Ingestion Pipeline (3 hours)

**Files to create**:

1. **`backend/app/layer2/data_ingestion/article_fetcher.py`**
```python
class ArticleIngestionService:
    def __init__(self):
        # Initialize mock data loader
        pass

    def fetch_articles(self, time_window=None):
        """Load articles from mock data files"""
        # Load from backend/mock_data/*.json
        pass

    def validate_article(self, article):
        """Validate article schema"""
        # Check required fields
        # Check data types
        pass

    def preprocess_article(self, article):
        """Clean and normalize article text"""
        # Text cleaning
        # Remove extra whitespace
        # Normalize unicode
        pass
```

2. **`backend/app/layer2/data_ingestion/validator.py`**
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ArticleContent(BaseModel):
    title: str
    body: str
    summary: Optional[str] = None

class ArticleMetadata(BaseModel):
    source: str
    source_credibility: float = Field(ge=0.0, le=1.0)
    publish_timestamp: datetime
    language_original: str = "en"

class ArticleSchema(BaseModel):
    article_id: str
    content: ArticleContent
    metadata: ArticleMetadata
    # ... other fields
```

**Deliverable**: Function that loads all 200 mock articles and returns validated list

**Test**:
```python
service = ArticleIngestionService()
articles = service.fetch_articles()
assert len(articles) >= 200
print(f"✅ Loaded {len(articles)} articles")
```

#### ✅ Task A2.2: Rule-Based Classification (4 hours)

**Files to create**:

1. **`backend/app/layer2/classification/rule_based.py`**
```python
class RuleBasedIndicatorAssigner:
    def __init__(self):
        # Load keyword mappings from database
        self.keyword_mappings = self._load_keyword_mappings()

    def assign_indicators(self, article):
        """Assign indicators based on keyword matching"""
        # Match keywords
        # Calculate confidence scores
        # Return list of indicator assignments
        pass

    def _calculate_match_score(self, article_text, keywords, rules):
        """Calculate how well article matches indicator"""
        pass
```

2. **`backend/scripts/populate_indicator_keywords.py`**

Define keywords for at least these 10 indicators:

| Indicator | Keywords |
|-----------|----------|
| Political Unrest | protest, strike, demonstration, hartal, walkout, civil unrest |
| Inflation Pressure | inflation, price increase, expensive, costly, rising prices |
| Currency Instability | LKR, exchange rate, depreciation, currency, forex |
| Consumer Confidence | spending, shopping, afford, buying, consumer |
| Supply Chain Issues | shortage, stock, inventory, import, supply chain |
| Tourism Activity | tourist, arrival, hotel, visit, tourism |
| Weather Severity | flood, drought, rain, storm, cyclone |
| Transport Disruption | road, traffic, closure, delay, transport |
| Power Outage | electricity, load shedding, power cut, outage |
| Healthcare Stress | hospital, medicine, shortage, treatment, healthcare |

**Deliverable**:
- Classify 200 articles
- Output indicator assignments with confidence scores
- Store in `article_indicator_mappings` table

**Test**:
```python
classifier = RuleBasedIndicatorAssigner()
article = articles[0]
assignments = classifier.assign_indicators(article)
print(f"✅ Article classified: {len(assignments)} indicators assigned")
```

#### ✅ Task A2.3: Integration Test (1 hour)

**File**: `backend/tests/integration/test_classification_pipeline.py`

Test complete flow:
```python
def test_classification_pipeline():
    # Load mock data
    articles = load_articles()

    # Classify
    classifier = RuleBasedIndicatorAssigner()
    for article in articles:
        assignments = classifier.assign_indicators(article)
        # Store in database

    # Verify database
    assert count_mappings() > 0
```

### Day 2 End (Developer A) ✅
- [ ] Article ingestion working (200 articles loaded)
- [ ] Rule-based classification implemented
- [ ] Keywords defined for 10+ indicators
- [ ] Mappings stored in database
- [ ] Integration test passing

---

## 👥 DEVELOPER B TASKS (Day 2)

### Your Focus: Database Models & Indicator Framework

#### ✅ Task B2.1: SQLAlchemy Models (2 hours)

**Files to create**:

1. **`backend/app/models/indicator.py`**
```python
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, TIMESTAMP
from app.db.base_class import Base

class IndicatorDefinition(Base):
    __tablename__ = "indicator_definitions"

    indicator_id = Column(Integer, primary_key=True)
    indicator_code = Column(String(100), unique=True, nullable=False)
    indicator_name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    pestel_category = Column(String(20), nullable=False)
    subcategory = Column(String(100))
    calculation_type = Column(String(50), nullable=False)
    # ... more fields

class IndicatorKeyword(Base):
    __tablename__ = "indicator_keywords"
    # ... fields

class IndicatorDependency(Base):
    __tablename__ = "indicator_dependencies"
    # ... fields

class IndicatorThreshold(Base):
    __tablename__ = "indicator_thresholds"
    # ... fields
```

2. **`backend/app/models/indicator_value.py`**
```python
class IndicatorValue(Base):
    __tablename__ = "indicator_values"
    # TimescaleDB hypertable
    # ... fields

class IndicatorEvent(Base):
    __tablename__ = "indicator_events"
    # ... fields

class IndicatorTrend(Base):
    __tablename__ = "indicator_trends"
    # ... fields
```

3. **`backend/app/models/article_mapping.py`**
```python
class ArticleIndicatorMapping(Base):
    __tablename__ = "article_indicator_mappings"

    mapping_id = Column(Integer, primary_key=True)
    article_id = Column(String(50), nullable=False)
    indicator_id = Column(Integer, ForeignKey("indicator_definitions.indicator_id"))
    match_confidence = Column(Float)
    # ... more fields
```

#### ✅ Task B2.2: Populate Indicator Definitions (3 hours)

**File**: `backend/scripts/populate_indicator_definitions.py`

Define **at least 24 indicators** across PESTEL categories:

**Political (5)**:
1. Cabinet Changes Frequency
2. Protest Frequency Index
3. Strike Activity Score
4. Public Dissatisfaction Index
5. Governance Risk Score

**Economic (8)**:
1. Consumer Confidence Proxy
2. Inflation Pressure Index
3. Currency Stability Indicator
4. Business Activity Index
5. Supply Chain Health
6. Tourism Activity Index
7. Stock Market Sentiment
8. Export Performance Index

**Social (4)**:
1. Overall Public Sentiment
2. Cost of Living Burden
3. Healthcare Access Index
4. Education Disruption Level

**Technological (2)**:
1. Internet Connectivity Status
2. Power Infrastructure Health

**Environmental (3)**:
1. Weather Severity Index
2. Flood Risk Level
3. Drought Concern Index

**Legal (2)**:
1. New Laws Frequency
2. Regulatory Change Rate

**Example definition**:
```python
{
    "indicator_code": "POL_UNREST_01",
    "indicator_name": "Protest Frequency Index",
    "display_name": "Political Unrest Level",
    "pestel_category": "Political",
    "subcategory": "Civil Unrest",
    "calculation_type": "frequency_count",
    "value_type": "index",
    "min_value": 0,
    "max_value": 100,
    "description": "Measures frequency and intensity of protests",
    "is_active": True
}
```

**Run script**:
```bash
python scripts/populate_indicator_definitions.py
```

#### ✅ Task B2.3: Indicator Calculation Framework (3 hours)

**Files to create**:

1. **`backend/app/layer2/indicators/calculator.py`**
```python
from abc import ABC, abstractmethod

class IndicatorCalculator(ABC):
    """Base class for all indicator calculators"""

    @abstractmethod
    def calculate(self, articles, **kwargs):
        """Calculate indicator value from articles"""
        pass

class FrequencyBasedCalculator(IndicatorCalculator):
    """Count-based indicators"""

    def calculate(self, articles, **kwargs):
        # Count articles
        # Compare to baseline
        # Return score
        pass

class SentimentBasedCalculator(IndicatorCalculator):
    """Sentiment aggregation indicators"""

    def calculate(self, articles, **kwargs):
        # Aggregate sentiment scores
        # Weight by credibility
        # Return score
        pass

class NumericExtractionCalculator(IndicatorCalculator):
    """Extract numeric values (prices, percentages)"""

    def calculate(self, articles, **kwargs):
        # Extract numbers from text
        # Aggregate
        # Return score
        pass
```

2. **`backend/app/layer2/indicators/registry.py`**
```python
class IndicatorRegistry:
    """Manages all indicators and their calculations"""

    def __init__(self):
        self.indicators = {}
        self._load_indicators()

    def get_indicator(self, indicator_id):
        """Get indicator definition"""
        pass

    def calculate_indicator(self, indicator_id, articles):
        """Calculate specific indicator"""
        pass

    def calculate_all(self, articles):
        """Calculate all active indicators"""
        pass
```

**Deliverable**: Framework ready to calculate indicators

**Test**:
```python
registry = IndicatorRegistry()
calculator = FrequencyBasedCalculator()
articles = get_articles_for_indicator("POL_UNREST_01")
value = calculator.calculate(articles)
print(f"✅ Protest Frequency Index: {value}")
```

### Day 2 End (Developer B) ✅
- [ ] All SQLAlchemy models created
- [ ] 24+ indicator definitions in database
- [ ] Calculation framework implemented
- [ ] Can calculate at least 1 simple indicator
- [ ] Test scripts working

---

## 🤝 DAY 2 INTEGRATION CHECKPOINT (Both - 30 mins)

**Meeting agenda**:
1. Developer A demo: Article loading + classification
2. Developer B demo: Indicator definitions + calculation framework
3. Integration test: Can we calculate a frequency-based indicator from classified articles?

**Test together**:
```python
# Developer A provides
articles = fetch_and_classify_articles()

# Developer B calculates
indicator_value = calculate_indicator("POL_UNREST_01", articles)

# Verify
assert indicator_value is not None
print(f"✅ Integration successful! Indicator value: {indicator_value}")
```

**Git**: Both create PRs, review each other, merge

---

## DAY 3: NLP COMPONENTS

---

## 👤 DEVELOPER A TASKS (Day 3)

### Your Focus: ML Classification System

#### ✅ Task A3.1: Training Data Preparation (2 hours)

**Files to create**:

1. **`backend/ml_training/training_data/labeled_articles.json`**

Manually label **100 articles** from your mock data:
```json
[
    {
        "article_id": "pol_001",
        "labels": [
            {"indicator_id": 2, "indicator_code": "POL_UNREST_01", "relevance": 0.95},
            {"indicator_id": 3, "indicator_code": "POL_STRIKE_01", "relevance": 0.85}
        ]
    }
]
```

**Labeling guide**:
- Relevance: 0.9-1.0 (highly relevant), 0.7-0.9 (relevant), 0.5-0.7 (somewhat relevant)
- Multi-label: One article can have multiple indicators
- Aim for balanced dataset (all indicators represented)

2. **`backend/app/layer2/classification/training_data_manager.py`**
```python
class TrainingDataManager:
    def load_training_data(self):
        """Load labeled articles"""
        pass

    def train_test_split(self, test_size=0.2):
        """Split into train/test sets"""
        pass

    def get_statistics(self):
        """Show label distribution"""
        pass
```

#### ✅ Task A3.2: ML Classifier Implementation (5 hours)

**File**: `backend/app/layer2/classification/ml_classifier.py`

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from xgboost import XGBClassifier
import pickle

class MLIndicatorClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        self.classifier = MultiOutputClassifier(
            XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1
            )
        )
        self.indicator_mapping = []
        self.is_trained = False

    def train(self, training_data):
        """Train on labeled articles"""
        # Prepare features (TF-IDF)
        # Prepare labels (binary matrix)
        # Train model
        # Evaluate (cross-validation)
        pass

    def predict(self, article):
        """Predict indicators for new article"""
        # Vectorize text
        # Get probabilities
        # Filter by threshold
        # Return predictions
        pass

    def save_model(self, path):
        """Save trained model"""
        with open(path, 'wb') as f:
            pickle.dump((self.vectorizer, self.classifier, self.indicator_mapping), f)

    def load_model(self, path):
        """Load trained model"""
        with open(path, 'rb') as f:
            self.vectorizer, self.classifier, self.indicator_mapping = pickle.load(f)
        self.is_trained = True
```

**Training script**: `backend/scripts/train_ml_classifier.py`
```python
# Load training data
training_data = load_labeled_articles()

# Train
classifier = MLIndicatorClassifier()
classifier.train(training_data)

# Evaluate
f1_score = classifier.evaluate(test_data)
print(f"F1 Score: {f1_score:.3f}")

# Save
classifier.save_model("ml_models/indicator_classifier_v1.pkl")
```

**Goal**: Achieve F1 score > 0.70

#### ✅ Task A3.3: Hybrid Classification (1 hour)

**File**: `backend/app/layer2/classification/hybrid.py`

```python
class HybridIndicatorAssigner:
    def __init__(self):
        self.rule_based = RuleBasedIndicatorAssigner()
        self.ml_classifier = MLIndicatorClassifier()
        self.ml_classifier.load_model("ml_models/indicator_classifier_v1.pkl")

    def assign_indicators(self, article):
        """Combine rule-based + ML predictions"""
        # Get both predictions
        rule_preds = self.rule_based.assign_indicators(article)
        ml_preds = self.ml_classifier.predict(article)

        # Merge (weighted combination)
        combined = self._merge_predictions(rule_preds, ml_preds)

        return combined

    def _merge_predictions(self, rule_preds, ml_preds):
        """
        Merge strategy:
        - Rule-based weight: 0.4
        - ML weight: 0.6
        - Boost if both agree: 1.2x
        """
        pass
```

### Day 3 End (Developer A) ✅
- [ ] 100 articles labeled
- [ ] ML classifier trained (F1 > 0.70)
- [ ] Model saved to disk
- [ ] Hybrid classifier implemented
- [ ] Can predict indicators for new articles

---

## 👥 DEVELOPER B TASKS (Day 3)

### Your Focus: Sentiment Analysis & Weighting

#### ✅ Task B3.1: Sentiment Analysis (3 hours)

**File**: `backend/app/layer2/nlp/sentiment_analyzer.py`

```python
from transformers import pipeline
import torch

class SentimentAnalyzer:
    def __init__(self):
        # Use pre-trained model
        self.model = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if torch.cuda.is_available() else -1
        )

    def analyze(self, text):
        """
        Analyze sentiment of text
        Returns: score from -1.0 (negative) to +1.0 (positive)
        """
        result = self.model(text[:512])  # Truncate to model limit

        # Convert to -1 to +1 scale
        label = result[0]['label']
        score = result[0]['score']

        if label == 'NEGATIVE':
            return -score
        else:
            return score

    def analyze_batch(self, texts):
        """Batch processing for efficiency"""
        pass
```

**Script**: `backend/scripts/add_sentiment_to_articles.py`
```python
# Load all mock articles
articles = load_all_articles()

# Analyze sentiment
analyzer = SentimentAnalyzer()
for article in articles:
    sentiment = analyzer.analyze(article['content']['body'])
    article['sentiment_score'] = sentiment
    # Update in database or file

print(f"✅ Added sentiment to {len(articles)} articles")
```

#### ✅ Task B3.2: Weighting System (3 hours)

**File**: `backend/app/layer2/indicators/weighting.py`

```python
from datetime import datetime
import math

def calculate_recency_weight(publish_timestamp):
    """
    More recent = higher weight
    Last 6 hours: 1.0
    1 day: 0.9
    3 days: 0.7
    1 week: 0.5
    Older: 0.3
    """
    age_hours = (datetime.now() - publish_timestamp).total_seconds() / 3600

    if age_hours < 6:
        return 1.0
    elif age_hours < 24:
        return 0.9
    elif age_hours < 72:
        return 0.7
    elif age_hours < 168:
        return 0.5
    else:
        return 0.3

def calculate_severity_weight(article_text):
    """
    Crisis keywords = higher severity
    Returns: 0.5 (normal) to 1.0 (crisis)
    """
    crisis_keywords = ['crisis', 'emergency', 'critical', 'urgent', 'breakdown', 'collapse']
    scale_keywords = ['nationwide', 'country-wide', 'widespread']

    severity = 0.5  # Base

    text_lower = article_text.lower()
    for keyword in crisis_keywords:
        if keyword in text_lower:
            severity += 0.1

    for keyword in scale_keywords:
        if keyword in text_lower:
            severity += 0.1

    return min(severity, 1.0)

def calculate_source_credibility_weight(article):
    """Use source credibility from article metadata"""
    return article['metadata']['source_credibility']

def calculate_volume_weight(article_count):
    """
    More articles = higher confidence
    1 article: 0.3
    10 articles: 0.7
    50 articles: 0.9
    100+: 1.0
    """
    if article_count >= 100:
        return 1.0
    elif article_count >= 50:
        return 0.9
    elif article_count >= 25:
        return 0.8
    elif article_count >= 10:
        return 0.7
    elif article_count >= 5:
        return 0.5
    else:
        return 0.3

def calculate_combined_weight(article, article_count):
    """
    Combine all weight factors
    Final = Recency × Severity × Credibility × Volume
    """
    recency = calculate_recency_weight(article['metadata']['publish_timestamp'])
    severity = calculate_severity_weight(article['content']['body'])
    credibility = calculate_source_credibility_weight(article)
    volume = calculate_volume_weight(article_count)

    return recency * severity * credibility * volume
```

#### ✅ Task B3.3: Update Calculators with Weights (2 hours)

**File**: `backend/app/layer2/indicators/calculator.py` (MODIFY)

```python
class FrequencyBasedCalculator(IndicatorCalculator):
    def calculate(self, articles, **kwargs):
        """Calculate with weighting"""
        total_weighted_score = 0
        total_weight = 0

        for article in articles:
            # Base contribution
            base_value = 1  # For frequency counting

            # Calculate weight
            weight = calculate_combined_weight(article, len(articles))

            # Accumulate
            total_weighted_score += base_value * weight
            total_weight += weight

        # Volume weight
        volume = calculate_volume_weight(len(articles))

        # Final score
        if total_weight > 0:
            weighted_avg = total_weighted_score / total_weight
            final_score = weighted_avg * volume * 100  # Scale to 0-100
        else:
            final_score = 0

        return final_score

class SentimentBasedCalculator(IndicatorCalculator):
    def calculate(self, articles, **kwargs):
        """Aggregate weighted sentiment"""
        total_weighted_sentiment = 0
        total_weight = 0

        for article in articles:
            # Get sentiment score
            sentiment = article.get('sentiment_score', 0)

            # Calculate weight
            weight = calculate_combined_weight(article, len(articles))

            # Accumulate
            total_weighted_sentiment += sentiment * weight
            total_weight += weight

        # Calculate final
        if total_weight > 0:
            avg_sentiment = total_weighted_sentiment / total_weight
            # Convert -1 to +1 → 0 to 100 scale
            score = ((avg_sentiment + 1) / 2) * 100
        else:
            score = 50  # Neutral

        return score
```

**Test**: Calculate 10 indicators with proper weighting

### Day 3 End (Developer B) ✅
- [ ] Sentiment analysis working
- [ ] All mock articles have sentiment scores
- [ ] Weighting system implemented
- [ ] Calculators updated with weighting
- [ ] 10+ indicators calculated with weights

---

## 🤝 DAY 3 INTEGRATION CHECKPOINT (Both - 30 mins)

**Test full pipeline**:
```python
# Load articles
articles = load_articles()

# Classify (Developer A - hybrid)
hybrid_classifier = HybridIndicatorAssigner()
for article in articles:
    article['assigned_indicators'] = hybrid_classifier.assign_indicators(article)

# Add sentiment (Developer B)
analyzer = SentimentAnalyzer()
for article in articles:
    article['sentiment_score'] = analyzer.analyze(article['content']['body'])

# Calculate indicators (Developer B - weighted)
registry = IndicatorRegistry()
results = registry.calculate_all(articles)

print(f"✅ Full pipeline test passed!")
print(f"Calculated {len(results)} indicators")
```

**Git**: Merge both features

---

## DAY 4: ADVANCED FEATURES

---

## 👤 DEVELOPER A TASKS (Day 4)

### Your Focus: Entity Extraction & MongoDB

#### ✅ Task A4.1: Entity Extraction (4 hours)

**File**: `backend/app/layer2/nlp/entity_extractor.py`

```python
import spacy
import re
from dateutil import parser as date_parser

class EntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

        # Regex patterns
        self.currency_pattern = re.compile(
            r'(?:Rs\.?|LKR|USD|\$)\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|mn|bn)?',
            re.IGNORECASE
        )
        self.percentage_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*%')

    def extract(self, text):
        """Extract all entities from text"""
        doc = self.nlp(text)

        entities = {
            'locations': [],
            'organizations': [],
            'persons': [],
            'dates': [],
            'amounts': []
        }

        # Use spaCy NER
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:
                entities['locations'].append({
                    'text': ent.text,
                    'type': 'location'
                })
            elif ent.label_ == 'ORG':
                entities['organizations'].append({
                    'text': ent.text,
                    'type': 'organization'
                })
            # ... more entity types

        # Extract amounts using regex
        for match in self.currency_pattern.finditer(text):
            entities['amounts'].append(self._parse_amount(match))

        return entities
```

**Script**: `backend/scripts/extract_entities_from_articles.py`

#### ✅ Task A4.2: Entity-Based Indicators (2 hours)

**File**: `backend/app/layer2/indicators/entity_based_calculator.py`

```python
def calculate_currency_stability_indicator(articles, entities_list):
    """Use extracted currency mentions"""
    currency_mentions = []
    negative_count = 0

    for article, entities in zip(articles, entities_list):
        for amount in entities['amounts']:
            if amount.get('currency') == 'LKR':
                sentiment = article.get('sentiment_score', 0)
                if sentiment < 0:
                    negative_count += 1
                currency_mentions.append({
                    'value': amount['value'],
                    'sentiment': sentiment
                })

    # Calculate instability score
    if len(currency_mentions) > 0:
        instability = (negative_count / len(currency_mentions)) * 100
    else:
        instability = 50  # Neutral

    return instability

def calculate_geographic_concentration(articles, entities_list):
    """Which regions are mentioned most"""
    location_counts = {}

    for entities in entities_list:
        for location in entities['locations']:
            loc_name = location['text']
            location_counts[loc_name] = location_counts.get(loc_name, 0) + 1

    sorted_locations = sorted(
        location_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        'top_locations': sorted_locations[:10],
        'total_unique': len(location_counts)
    }
```

#### ✅ Task A4.3: MongoDB Integration (2 hours)

**File**: `backend/app/db/mongodb.py`

```python
from pymongo import MongoClient
from app.core.config import settings

class MongoDBManager:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client.national_indicator

        # Collections
        self.indicator_calculations = self.db.indicator_calculations
        self.indicator_narratives = self.db.indicator_narratives
        self.entity_extractions = self.db.entity_extractions

    def store_calculation_details(self, indicator_id, calculation_data):
        """Store detailed calculation breakdown"""
        self.indicator_calculations.insert_one(calculation_data)

    def store_entities(self, article_id, entities):
        """Store extracted entities"""
        self.entity_extractions.insert_one({
            'article_id': article_id,
            'entities': entities,
            'extracted_at': datetime.now()
        })
```

### Day 4 End (Developer A) ✅
- [ ] Entity extraction working
- [ ] Entities extracted from all 200 articles
- [ ] 2+ entity-based indicators implemented
- [ ] MongoDB integration complete
- [ ] Entities stored in MongoDB

---

## 👥 DEVELOPER B TASKS (Day 4)

### Your Focus: Composite Indicators & Caching

#### ✅ Task B4.1: Composite Indicators (3 hours)

**File**: `backend/app/layer2/indicators/composite_calculator.py`

```python
class CompositeIndicatorCalculator:
    def calculate_economic_health_index(self):
        """
        Composite of economic sub-indicators
        """
        # Get component values
        consumer_conf = get_indicator_value('consumer_confidence_proxy')
        business_act = get_indicator_value('business_activity_index')
        supply_chain = get_indicator_value('supply_chain_health')
        currency = get_indicator_value('currency_stability')
        inflation = get_indicator_value('inflation_pressure_index')

        # Weighted average
        economic_health = (
            0.30 * consumer_conf +
            0.25 * business_act +
            0.20 * supply_chain +
            0.15 * currency +
            0.10 * (100 - inflation)  # Invert inflation
        )

        return {
            'value': economic_health,
            'components': {
                'consumer_confidence': consumer_conf,
                'business_activity': business_act,
                'supply_chain': supply_chain,
                'currency_sentiment': currency,
                'inflation_pressure': inflation
            }
        }

    def calculate_national_stability_score(self):
        """Overall stability composite"""
        political = get_indicator_value('political_stability_index')
        economic = self.calculate_economic_health_index()['value']
        social = get_indicator_value('public_sentiment_index')

        stability = (
            0.4 * political +
            0.3 * economic +
            0.3 * social
        )

        return stability
```

#### ✅ Task B4.2: Dependency Mapping (2 hours)

**File**: `backend/app/layer2/analysis/dependency_mapper.py`

```python
class IndicatorDependencyEngine:
    def __init__(self):
        self.dependencies = self._load_dependencies_from_db()

    def get_affected_indicators(self, indicator_id):
        """Find which indicators this one affects"""
        affected = []
        for dep in self.dependencies:
            if dep['child'] == indicator_id:
                affected.append(dep['parent'])
        return affected

    def predict_secondary_effects(self, indicator_id, current_value, change):
        """Predict cascading impacts"""
        affected = self.get_affected_indicators(indicator_id)
        predictions = []

        for affected_id in affected:
            # Get dependency strength
            dep = self._get_dependency(indicator_id, affected_id)
            correlation = dep['correlation_strength']

            # Predict change
            predicted_change = change * correlation

            predictions.append({
                'indicator_id': affected_id,
                'expected_change': predicted_change,
                'confidence': abs(correlation)
            })

        return predictions
```

#### ✅ Task B4.3: Populate Dependencies (2 hours)

**File**: `backend/scripts/populate_dependencies.py`

Define key relationships:
```python
dependencies = [
    {
        'parent': 'transport_disruption',
        'child': 'fuel_shortage_index',
        'relationship': 'causes',
        'time_lag_hours': 48,
        'correlation_strength': 0.85
    },
    {
        'parent': 'consumer_confidence',
        'child': 'fuel_shortage_index',
        'relationship': 'causes',
        'time_lag_hours': 72,
        'correlation_strength': -0.65  # Negative correlation
    },
    # Add 10+ dependencies
]
```

#### ✅ Task B4.4: Redis Caching (1 hour)

**File**: `backend/app/db/redis_manager.py`

```python
import redis
import json
from app.core.config import settings

class RedisCache:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    def set_indicator_value(self, indicator_id, value, ttl=300):
        """Cache indicator value (TTL 5 minutes)"""
        key = f"indicator:current:{indicator_id}"
        self.redis.setex(key, ttl, json.dumps(value))

    def get_indicator_value(self, indicator_id):
        """Get cached indicator value"""
        key = f"indicator:current:{indicator_id}"
        value = self.redis.get(key)
        return json.loads(value) if value else None

    def invalidate_indicator(self, indicator_id):
        """Clear cache for indicator"""
        key = f"indicator:current:{indicator_id}"
        self.redis.delete(key)
```

### Day 4 End (Developer B) ✅
- [ ] 2+ composite indicators working
- [ ] Dependency engine implemented
- [ ] 10+ dependencies defined in DB
- [ ] Redis caching operational
- [ ] Can predict secondary effects

---

## 🤝 DAY 4 INTEGRATION CHECKPOINT

**Test composite indicator calculation**:
```python
composite_calc = CompositeIndicatorCalculator()
economic_health = composite_calc.calculate_economic_health_index()
print(f"✅ Economic Health Index: {economic_health['value']:.2f}")
print(f"Components: {economic_health['components']}")
```

**Git**: Merge features

---

## DAY 5: TIME SERIES ANALYSIS

---

## 👤 DEVELOPER A TASKS (Day 5)

### Your Focus: Trends & Forecasting

#### ✅ Task A5.1: Historical Data Generation (1 hour)

**File**: `backend/scripts/generate_historical_data.py`

```python
import numpy as np
from datetime import datetime, timedelta

def generate_historical_indicator_values(indicator_id, days=90):
    """Generate realistic time-series data"""

    # Different trend patterns
    patterns = ['rising', 'falling', 'stable', 'volatile']
    pattern = np.random.choice(patterns)

    values = []
    base_value = 50  # Start at 50

    for day in range(days):
        timestamp = datetime.now() - timedelta(days=days-day)

        if pattern == 'rising':
            trend = day * 0.3
            noise = np.random.normal(0, 2)
            value = base_value + trend + noise
        elif pattern == 'falling':
            trend = -day * 0.3
            noise = np.random.normal(0, 2)
            value = base_value + trend + noise
        elif pattern == 'volatile':
            value = base_value + np.random.normal(0, 10)
        else:  # stable
            value = base_value + np.random.normal(0, 3)

        # Clip to valid range
        value = np.clip(value, 0, 100)

        values.append({
            'timestamp': timestamp,
            'indicator_id': indicator_id,
            'value': value
        })

    return values

# Generate for all indicators
for indicator_id in range(1, 25):  # 24 indicators
    historical_values = generate_historical_indicator_values(indicator_id)
    # Insert into indicator_values table
```

#### ✅ Task A5.2: Trend Detection (4 hours)

**File**: `backend/app/layer2/analysis/trend_detector.py`

```python
import numpy as np
from scipy import stats

class TrendDetector:
    def calculate_moving_averages(self, indicator_id, periods=[7, 30, 90]):
        """Calculate multiple moving averages"""
        mas = {}

        for period in periods:
            values = get_historical_values(indicator_id, days=period)
            if len(values) >= period:
                ma = np.mean([v['value'] for v in values[-period:]])
                mas[f'ma_{period}day'] = ma

        return mas

    def detect_trend(self, indicator_id, window_days=30):
        """
        Detect trend direction and strength
        Returns: {'direction': str, 'strength': float, 'slope': float}
        """
        values = get_historical_values(indicator_id, days=window_days)

        if len(values) < 5:
            return {'direction': 'unknown', 'strength': 0}

        # Linear regression
        x = np.arange(len(values))
        y = np.array([v['value'] for v in values])

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Determine direction
        if slope > 0.5:
            direction = 'rising'
        elif slope < -0.5:
            direction = 'falling'
        else:
            direction = 'stable'

        strength = r_value ** 2  # R-squared

        return {
            'direction': direction,
            'strength': strength,
            'slope': slope,
            'r_squared': strength,
            'rate_of_change': (values[-1]['value'] - values[0]['value']) / window_days
        }
```

#### ✅ Task A5.3: Forecasting (3 hours)

**File**: `backend/app/layer2/analysis/forecaster.py`

```python
class Forecaster:
    def forecast_linear(self, indicator_id, days_ahead=7):
        """Simple linear extrapolation"""
        # Get last 30 days
        values = get_historical_values(indicator_id, days=30)

        if len(values) < 10:
            return None

        # Fit linear model
        x = np.arange(len(values))
        y = np.array([v['value'] for v in values])
        slope, intercept = np.polyfit(x, y, 1)

        # Project forward
        forecasts = []
        for i in range(1, days_ahead + 1):
            future_x = len(values) + i
            forecast_value = slope * future_x + intercept

            # Confidence interval (simple)
            residuals = y - (slope * x + intercept)
            std_error = np.std(residuals)

            forecasts.append({
                'days_ahead': i,
                'forecast_value': forecast_value,
                'lower_bound': forecast_value - 2 * std_error,
                'upper_bound': forecast_value + 2 * std_error
            })

        return forecasts
```

**Script**: `backend/scripts/calculate_all_trends_and_forecasts.py`

### Day 5 End (Developer A) ✅
- [ ] 90 days of historical data for all indicators
- [ ] Trend detection working
- [ ] Moving averages calculated
- [ ] 7-day forecasts generated
- [ ] Results stored in indicator_trends table

---

## 👥 DEVELOPER B TASKS (Day 5)

### Your Focus: Anomaly Detection & Alerts

#### ✅ Task B5.1: Anomaly Detection (3 hours)

**File**: `backend/app/layer2/analysis/anomaly_detector.py`

```python
class AnomalyDetector:
    def detect_anomalies(self, indicator_id, current_value):
        """Statistical anomaly detection (z-score)"""
        # Get historical distribution (90 days)
        historical = get_historical_values(indicator_id, days=90)
        historical_values = [v['value'] for v in historical]

        # Calculate statistics
        mean = np.mean(historical_values)
        std = np.std(historical_values)

        # Z-score
        z_score = (current_value - mean) / std if std > 0 else 0

        # Anomaly if |z| > 2
        is_anomaly = abs(z_score) > 2

        # Severity
        if abs(z_score) > 3:
            severity = 'extreme'
        elif abs(z_score) > 2:
            severity = 'significant'
        else:
            severity = 'normal'

        return {
            'is_anomaly': is_anomaly,
            'severity': severity,
            'z_score': z_score,
            'current_value': current_value,
            'expected_value': mean,
            'deviation': current_value - mean
        }

    def detect_spike(self, indicator_id):
        """Detect rapid changes (24 hour)"""
        current = get_current_value(indicator_id)
        value_24h_ago = get_value_at(indicator_id, hours_ago=24)

        absolute_change = current - value_24h_ago
        percentage_change = (absolute_change / value_24h_ago * 100) if value_24h_ago != 0 else 0

        is_spike = abs(percentage_change) > 50

        return {
            'is_spike': is_spike,
            'absolute_change': absolute_change,
            'percentage_change': percentage_change,
            'direction': 'upward' if absolute_change > 0 else 'downward'
        }
```

#### ✅ Task B5.2: Event Logging (2 hours)

**File**: `backend/app/layer2/analysis/event_logger.py`

```python
class EventLogger:
    def log_event(self, indicator_id, event_type, event_data):
        """Log significant indicator events"""
        event = {
            'time': datetime.now(),
            'indicator_id': indicator_id,
            'event_type': event_type,  # 'anomaly', 'threshold_breach', 'rapid_change'
            'event_severity': event_data['severity'],
            'current_value': event_data['current_value'],
            'description': self._generate_description(event_type, event_data)
        }

        # Insert into indicator_events table
        insert_event(event)

        return event

    def _generate_description(self, event_type, data):
        """Generate human-readable description"""
        if event_type == 'anomaly_detected':
            return f"Anomaly detected: value {data['current_value']:.1f} is {abs(data['deviation']):.1f} points from expected {data['expected_value']:.1f}"
        # ... more types
```

#### ✅ Task B5.3: Alert System (3 hours)

**File**: `backend/app/layer2/alerting/alert_manager.py`

```python
class AlertManager:
    def check_thresholds(self, indicator_id, current_value):
        """Check if value breaches thresholds"""
        thresholds = get_indicator_thresholds(indicator_id)

        alerts = []
        for threshold in thresholds:
            if threshold['min_value'] <= current_value <= threshold['max_value']:
                if threshold['should_alert']:
                    alerts.append({
                        'indicator_id': indicator_id,
                        'alert_type': 'threshold_breach',
                        'severity': threshold['level_name'],
                        'message': threshold['alert_message_template'].format(value=current_value)
                    })

        return alerts

    def generate_alerts(self):
        """Check all indicators and generate alerts"""
        all_alerts = []

        # Get all current indicator values
        indicators = get_all_current_indicators()

        for indicator in indicators:
            # Check thresholds
            threshold_alerts = self.check_thresholds(
                indicator['indicator_id'],
                indicator['current_value']
            )
            all_alerts.extend(threshold_alerts)

            # Check anomalies
            anomaly = detect_anomalies(indicator['indicator_id'], indicator['current_value'])
            if anomaly['is_anomaly']:
                all_alerts.append({
                    'indicator_id': indicator['indicator_id'],
                    'alert_type': 'anomaly_detected',
                    'severity': anomaly['severity'],
                    'message': f"Anomaly: {indicator['indicator_name']} is {anomaly['severity']}"
                })

        # Store alerts
        for alert in all_alerts:
            store_alert(alert)

        return all_alerts
```

### Day 5 End (Developer B) ✅
- [ ] Anomaly detection implemented (z-score method)
- [ ] Spike detection working
- [ ] Event logger functional
- [ ] Alert system operational
- [ ] Alerts generated for current indicators

---

## 🤝 DAY 5 INTEGRATION CHECKPOINT

**Test complete analytics**:
```python
# Generate alerts
alert_mgr = AlertManager()
alerts = alert_mgr.generate_alerts()
print(f"✅ Generated {len(alerts)} alerts")

# Get trends
trend_detector = TrendDetector()
for indicator_id in range(1, 25):
    trend = trend_detector.detect_trend(indicator_id)
    print(f"Indicator {indicator_id}: {trend['direction']} trend")

# Forecasts
forecaster = Forecaster()
forecast = forecaster.forecast_linear(1, days_ahead=7)
print(f"7-day forecast: {forecast}")
```

**Git**: Merge features

---

## DAYS 6-7: INTEGRATION & POLISH (Both Together)

---

## DAY 6: INTEGRATION (Pair Programming)

### Morning (Both - 4 hours)

#### ✅ Task 6.1: Narrative Generation (2 hours)

**File**: `backend/app/layer2/narrative/generator.py`

```python
class IndicatorNarrativeGenerator:
    def generate_narrative(self, indicator_id):
        """Generate human-readable explanation"""
        # Get data
        indicator = get_indicator_definition(indicator_id)
        current_value = get_current_value(indicator_id)
        trend = detect_trend(indicator_id)
        anomaly = detect_anomalies(indicator_id, current_value)
        articles = get_contributing_articles(indicator_id)

        # Build narrative
        headline = self._generate_headline(indicator, current_value, trend, anomaly)
        summary = self._generate_summary(indicator, current_value, trend, len(articles))

        narrative = {
            'indicator_id': indicator_id,
            'timestamp': datetime.now(),
            'headline': headline,
            'summary': summary,
            'current_value': current_value,
            'trend_direction': trend['direction']
        }

        # Store in MongoDB
        store_narrative(narrative)

        return narrative

    def _generate_headline(self, indicator, value, trend, anomaly):
        """Generate attention-grabbing headline"""
        name = indicator['display_name']

        if anomaly['is_anomaly'] and anomaly['severity'] == 'extreme':
            return f"⚠️ {name} Reaches Extreme Level"
        elif trend['direction'] == 'rising' and trend['strength'] > 0.7:
            return f"📈 {name} Shows Strong Upward Trend"
        elif trend['direction'] == 'falling' and trend['strength'] > 0.7:
            return f"📉 {name} Declining Significantly"
        else:
            return f"{name}: Current Status"
```

#### ✅ Task 6.2: API Endpoints (2 hours)

**File**: `backend/app/api/v1/endpoints/indicators.py`

```python
from fastapi import APIRouter, HTTPException
from typing import List, Optional

router = APIRouter()

@router.get("/indicators")
def get_all_indicators():
    """List all indicators with current values"""
    indicators = get_all_current_indicators()
    return indicators

@router.get("/indicators/{indicator_id}")
def get_indicator(indicator_id: int):
    """Get specific indicator details"""
    indicator = get_indicator_definition(indicator_id)
    current_value = get_current_value(indicator_id)
    trend = detect_trend(indicator_id)
    narrative = get_latest_narrative(indicator_id)

    return {
        'indicator': indicator,
        'current_value': current_value,
        'trend': trend,
        'narrative': narrative
    }

@router.get("/indicators/{indicator_id}/history")
def get_indicator_history(indicator_id: int, days: int = 30):
    """Get time-series data"""
    history = get_historical_values(indicator_id, days=days)
    return history

@router.get("/indicators/trends")
def get_trending_indicators(direction: str = "all"):
    """Get indicators with strong trends"""
    trending = []
    for indicator_id in range(1, 25):
        trend = detect_trend(indicator_id)
        if direction == "all" or trend['direction'] == direction:
            if trend['strength'] > 0.7:
                trending.append({
                    'indicator_id': indicator_id,
                    'trend': trend
                })
    return trending

@router.get("/indicators/anomalies")
def get_anomalous_indicators():
    """Get indicators with detected anomalies"""
    anomalies = []
    for indicator_id in range(1, 25):
        current_value = get_current_value(indicator_id)
        anomaly = detect_anomalies(indicator_id, current_value)
        if anomaly['is_anomaly']:
            anomalies.append({
                'indicator_id': indicator_id,
                'anomaly': anomaly
            })
    return anomalies

@router.get("/indicators/alerts")
def get_active_alerts():
    """Get current alerts"""
    alerts = get_recent_alerts(hours=24)
    return alerts

@router.get("/indicators/composite")
def get_composite_indicators():
    """Get composite indicators"""
    composite_calc = CompositeIndicatorCalculator()

    economic_health = composite_calc.calculate_economic_health_index()
    national_stability = composite_calc.calculate_national_stability_score()

    return {
        'economic_health_index': economic_health,
        'national_stability_score': national_stability
    }
```

**Update**: `backend/app/api/v1/router.py`

### Afternoon (Both - 4 hours)

#### ✅ Task 6.3: Integration Testing (2 hours)

**File**: `backend/tests/integration/test_layer2_pipeline.py`

```python
def test_full_pipeline():
    """Test complete end-to-end flow"""
    # 1. Load articles
    articles = load_mock_articles()
    assert len(articles) >= 200

    # 2. Classify
    hybrid = HybridIndicatorAssigner()
    for article in articles:
        article['indicators'] = hybrid.assign_indicators(article)

    # 3. Add sentiment
    analyzer = SentimentAnalyzer()
    for article in articles:
        article['sentiment'] = analyzer.analyze(article['content']['body'])

    # 4. Extract entities
    extractor = EntityExtractor()
    for article in articles:
        article['entities'] = extractor.extract(article['content']['body'])

    # 5. Calculate indicators
    registry = IndicatorRegistry()
    results = registry.calculate_all(articles)
    assert len(results) >= 20

    # 6. Check trends
    trend_detector = TrendDetector()
    trends = trend_detector.detect_trend(1)
    assert 'direction' in trends

    # 7. Check anomalies
    anomaly_detector = AnomalyDetector()
    anomaly = anomaly_detector.detect_anomalies(1, 75)
    assert 'is_anomaly' in anomaly

    # 8. API test
    response = client.get("/api/v1/indicators")
    assert response.status_code == 200

    print("✅ Full pipeline integration test passed!")
```

#### ✅ Task 6.4: Performance Optimization (2 hours)

**Tasks**:
1. Add database indexes:
```sql
CREATE INDEX idx_indicator_values_indicator_time ON indicator_values(indicator_id, time DESC);
CREATE INDEX idx_article_mappings_article ON article_indicator_mappings(article_id);
CREATE INDEX idx_article_mappings_indicator ON article_indicator_mappings(indicator_id);
```

2. Optimize queries (use `joinedload`)
3. Enable Redis caching for all indicator queries
4. Batch inserts for historical data

**Test performance**:
```python
import time

start = time.time()
results = registry.calculate_all(articles)
end = time.time()

print(f"Calculated {len(results)} indicators in {end-start:.2f} seconds")
assert (end - start) < 10  # Should be under 10 seconds
```

### Day 6 End ✅
- [ ] Narrative generation working
- [ ] All API endpoints functional
- [ ] Integration tests passing
- [ ] Performance optimized
- [ ] Full pipeline working end-to-end

**Git**: Merge integration work

---

## DAY 7: POLISH & DOCUMENTATION (Both Together)

### Morning (4 hours)

#### ✅ Task 7.1: Simple Dashboard (2 hours)

**File**: `backend/app/static/index.html`

Create basic HTML dashboard:
- Display all indicators with current values
- Show trends (↑ ↓ ↔ arrows)
- Highlight anomalies (red color)
- Simple charts (Chart.js)

#### ✅ Task 7.2: Testing (2 hours)

**Files**:
- `backend/tests/unit/test_calculators.py`
- `backend/tests/unit/test_classifiers.py`
- `backend/tests/unit/test_sentiment.py`
- `backend/tests/integration/test_api.py`

**Run tests**:
```bash
pytest backend/tests/ -v --cov=app/layer2
```

**Goal**: 80%+ test coverage

### Afternoon (4 hours)

#### ✅ Task 7.3: Documentation (2 hours)

**Files to create/update**:

1. **`README.md`**
```markdown
# National Activity Indicator - Layer 2

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Start databases: `docker-compose up -d`
3. Run migrations: `alembic upgrade head`
4. Populate data: `python scripts/populate_indicator_definitions.py`
5. Start server: `uvicorn app.main:app --reload`

## API
- GET /api/v1/indicators - List all indicators
- GET /api/v1/indicators/{id} - Get specific indicator
- GET /api/v1/indicators/alerts - Get active alerts
...
```

2. **`docs/LAYER2_ARCHITECTURE.md`** - System design document
3. **`docs/INDICATOR_GUIDE.md`** - All indicators explained
4. **`docs/API_DOCUMENTATION.md`** - Complete API reference
5. **`docs/DEPLOYMENT.md`** - Deployment guide

#### ✅ Task 7.4: Deployment Prep (1 hour)

- Update `docker-compose.yml` for production
- Environment variable management
- Health check endpoints

#### ✅ Task 7.5: Demo Preparation (1 hour)

- Prepare demo script
- Generate sample outputs
- Create presentation slides (optional)

### Day 7 End ✅
- [ ] Simple dashboard working
- [ ] 80%+ test coverage
- [ ] Complete documentation
- [ ] Production-ready Docker setup
- [ ] Demo ready

**Git**: Final merge, tag as `v1.0-layer2-complete`

---

## FINAL SUCCESS CHECKLIST

By end of Day 7, you should have:

### Infrastructure ✅
- [ ] Docker Compose with all databases
- [ ] Database schemas created (PostgreSQL/TimescaleDB, MongoDB)
- [ ] All dependencies installed
- [ ] Project structure complete

### Data ✅
- [ ] 200+ mock articles generated
- [ ] All articles classified (hybrid)
- [ ] Sentiment scores added
- [ ] Entities extracted

### Indicators ✅
- [ ] 24+ indicator definitions
- [ ] Rule-based classification working
- [ ] ML classifier trained (F1 > 0.70)
- [ ] Hybrid classification implemented
- [ ] Weighting system functional
- [ ] 20+ indicators calculating correctly
- [ ] 2+ composite indicators working

### Time Series ✅
- [ ] 90 days of historical data
- [ ] Trend detection working
- [ ] Moving averages calculated
- [ ] 7-day forecasts generated
- [ ] Anomaly detection operational
- [ ] Alert system functional

### Advanced Features ✅
- [ ] Entity extraction working
- [ ] Entity-based indicators implemented
- [ ] Dependency mapping complete
- [ ] Redis caching operational
- [ ] MongoDB integration complete
- [ ] Narrative generation working

### API & Integration ✅
- [ ] Complete API for Layer 3
- [ ] All endpoints tested
- [ ] Integration tests passing
- [ ] Performance optimized

### Documentation ✅
- [ ] README complete
- [ ] Architecture documented
- [ ] API documentation
- [ ] Deployment guide
- [ ] Demo ready

---

## TIPS FOR SUCCESS

### For Developer A (You):
- **Day 1**: Focus on getting mock data generator working perfectly - this is critical for Day 2-5
- **Day 2**: Rule-based classification is straightforward, don't overthink it
- **Day 3**: ML classifier - start simple (TF-IDF + Logistic Regression), optimize later if needed
- **Day 4**: Entity extraction with spaCy is well-documented, follow examples
- **Day 5**: Historical data generation - use numpy for realistic patterns

### For Developer B (Team Member):
- **Day 1**: Database models are tedious but important - use AI agents to generate boilerplate
- **Day 2**: Indicator definitions - copy from blueprint, customize as needed
- **Day 3**: Sentiment analysis - use pre-trained model, don't train from scratch
- **Day 4**: Composite indicators are just weighted averages - keep it simple
- **Day 5**: Anomaly detection - z-score method is tried and tested

### For Both:
- **Communication is key** - daily standups are non-negotiable
- **Test as you go** - don't wait until Day 6 to test integration
- **Use AI agents** - for boilerplate, mock data, test generation
- **Don't over-engineer** - focus on getting it working first, optimize later
- **Commit often** - small, frequent commits avoid merge conflicts
- **Document as you code** - don't leave it all for Day 7

---

## CONTACT & COORDINATION

**Daily Standup**: 9 AM (15 mins)
- What did you complete yesterday?
- What are you working on today?
- Any blockers?

**Integration Checkpoints**: End of Day 1, 3, 5
- Demo what you built
- Test integration together
- Merge code

**Emergency Contact**: Set up a shared Slack/Discord channel for quick questions

---

Good luck with the implementation! 🚀
