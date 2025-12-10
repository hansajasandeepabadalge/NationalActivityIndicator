# LAYER 2 AI/LLM ENHANCEMENT PLAN
## Intelligent National Indicator Engine with Advanced AI Integration

---

## EXECUTIVE SUMMARY

### **Goal:** Enhance Layer 2 with AI/LLM to achieve 90%+ accuracy, intelligent processing, and adaptive indicators

### **Current vs Enhanced:**

```
BEFORE (Basic):                    AFTER (AI-Enhanced):
├── Rule-based classification      ├── LLM multi-label classification
├── Simple sentiment (-1 to 1)     ├── Multi-dimensional sentiment  
├── Basic NER                      ├── Entity relationships + linking
├── Keyword extraction             ├── Semantic topic modeling
├── Fixed indicator weights        ├── Adaptive weight adjustment
└── No validation                  └── Multi-source validation + quality scoring
```

### **Technology:** Groq Llama 3.1 70B (FREE) + LangChain + ChromaDB

---

## 7 KEY ENHANCEMENTS

### **Enhancement 1: LLM-Powered Classification**
- **What:** Replace rule-based with Groq LLM classification
- **Accuracy:** 75% → 90%+
- **Output:** Primary category, sub-themes, confidence, urgency, business relevance
- **Cost:** $0 (Groq free tier)

### **Enhancement 2: Advanced Sentiment Analysis**
- **What:** Multi-dimensional sentiment (overall, business confidence, public mood, economic)
- **Accuracy:** 70% → 85%+
- **Output:** 4 sentiment dimensions + drivers + confidence

### **Enhancement 3: Smart Entity Recognition**
- **What:** LLM entity extraction + relationships + historical tracking
- **Accuracy:** 80% recall → 90%+ recall
- **Output:** Entities with roles, relationships, sentiment, importance

### **Enhancement 4: Contextual Topic Modeling**
- **What:** Semantic topics + trend detection + ChromaDB clustering
- **Output:** Main topics, emerging topics, topic evolution

### **Enhancement 5: Multi-Source Validation**
- **What:** Cross-validate facts across articles
- **Output:** Confidence scores based on source consensus

### **Enhancement 6: Adaptive Indicator Calculation**
- **What:** LLM suggests weight adjustments based on context
- **Output:** Dynamic weights + anomaly detection

### **Enhancement 7: Quality Scoring**
- **What:** 0-100 quality score for all outputs
- **Output:** Overall quality + dimension scores
- **Use:** Filter low-quality data from indicators

---

## DATABASE SCHEMA UPDATES

```sql
-- Add to processed_articles table
ALTER TABLE processed_articles
-- Classification enhancements
ADD COLUMN classification_confidence FLOAT,
ADD COLUMN sub_themes TEXT[],
ADD COLUMN urgency_level VARCHAR(20),
ADD COLUMN business_relevance INTEGER,
ADD COLUMN classification_reasoning TEXT,

-- Sentiment enhancements
ADD COLUMN sentiment_overall VARCHAR(20),
ADD COLUMN business_confidence_impact INTEGER,
ADD COLUMN public_mood INTEGER,
ADD COLUMN economic_sentiment INTEGER,
ADD COLUMN sentiment_drivers TEXT[],

-- Quality scoring
ADD COLUMN overall_quality_score FLOAT,
ADD COLUMN quality_band VARCHAR(20);

-- New tables
CREATE TABLE entity_master (
    id SERIAL PRIMARY KEY,
    canonical_name VARCHAR(200) UNIQUE,
    entity_type VARCHAR(50),
    aliases TEXT[],
    mention_count INTEGER
);

CREATE TABLE article_entities (
    article_id INTEGER REFERENCES processed_articles(id),
    entity_id INTEGER REFERENCES entity_master(id),
    context TEXT,
    relationships JSONB,
    importance INTEGER
);

CREATE TABLE topic_trends (
    topic_name VARCHAR(200),
    date DATE,
    mention_count INTEGER,
    velocity FLOAT,
    is_trending BOOLEAN
);

CREATE TABLE classification_cache (
    content_hash VARCHAR(64) PRIMARY KEY,
    classification JSONB,
    created_at TIMESTAMP,
    hits INTEGER DEFAULT 1
);
```

---

## IMPLEMENTATION INSTRUCTIONS

### **Step 1: LLM Classification Service**

**File:** `layer2/services/llm_classifier.py`

```python
# Essential structure only - AI agent will implement details

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
import hashlib
import redis

class LLMClassifier:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0.2
        )
        self.cache = redis.Redis()
    
    def classify(self, article):
        """
        Classify article using LLM
        
        Returns:
        {
            "primary_category": "Economic",
            "secondary_categories": ["Political"],
            "sub_themes": ["inflation", "monetary policy"],
            "confidence": 92,
            "reasoning": "...",
            "urgency": "high",
            "business_relevance": 95
        }
        """
        # Check cache first
        cache_key = hashlib.md5(article['content'].encode()).hexdigest()
        
        # If not cached, call LLM
        # Use structured output prompt
        # Parse and validate response
        # Cache result
        # Return classification
```

**LLM Prompt:**
```yaml
System: "Expert analyst classifying Sri Lankan news into PESTEL framework"

User Template:
  Title: {title}
  Content: {content}
  Source: {source}
  
  Classify this article:
  1. Primary PESTEL category (Political/Economic/Social/Technological/Environmental/Legal)
  2. Secondary categories if applicable (max 2)
  3. Specific sub-themes (3-5 keywords)
  4. Confidence score (0-100)
  5. Urgency level (low/medium/high/critical)
  6. Business relevance score (0-100)
  7. Brief reasoning (1-2 sentences)
  
  Output as JSON.

Expected Response:
  {
    "primary_category": "Economic",
    "secondary_categories": ["Political"],
    "sub_themes": ["inflation", "interest rates", "monetary policy"],
    "confidence": 92,
    "urgency": "high",
    "business_relevance": 95,
    "reasoning": "Central Bank policy changes directly impact business costs"
  }
```

---

### **Step 2: Advanced Sentiment Analyzer**

**File:** `layer2/services/advanced_sentiment.py`

```python
class AdvancedSentimentAnalyzer:
    def analyze(self, article):
        """
        Multi-dimensional sentiment analysis
        
        Returns:
        {
            "overall_sentiment": "negative",
            "sentiment_score": -0.65,
            "business_confidence_impact": -45,
            "public_mood": -60,
            "economic_sentiment": -70,
            "sentiment_drivers": ["fuel price increase", "inflation"],
            "confidence": 88
        }
        """
        # Quick check with spaCy first
        # If neutral (-0.1 to 0.1): skip LLM, use basic
        # Otherwise: call LLM for deep analysis
        # Combine results
        # Return multi-dimensional sentiment
```

**LLM Prompt:**
```yaml
System: "Sentiment analyst specializing in business impact"

User Template:
  Article: {title} - {content}
  
  Analyze sentiment across:
  1. Overall: -1 (very negative) to 1 (very positive)
  2. Business Confidence Impact: -100 to 100
  3. Public Mood: -100 to 100
  4. Economic Sentiment: -100 to 100
  5. Key Drivers: What phrases/facts drive this sentiment?
  
  Output as JSON with scores and brief explanation.
```

---

### **Step 3: Smart Entity Extractor**

**File:** `layer2/services/entity_extractor.py`

```python
class SmartEntityExtractor:
    def extract_and_link(self, article):
        """
        Extract entities with relationships and link to master table
        
        Returns:
        [
            {
                "name": "Ranil Wickremesinghe",
                "type": "PERSON",
                "role": "President",
                "relationships": [
                    {"entity": "Government", "type": "heads"}
                ],
                "sentiment": "neutral",
                "importance": 85
            }
        ]
        """
        # Call LLM to extract entities
        # For each entity, check entity_master table
        # Use fuzzy matching to find existing
        # If new: add to master
        # If existing: update mention count
        # Return entities with master IDs
```

**Entity Resolution:**
```python
def resolve_entity(entity_name, entity_type):
    """
    Match entity to master table using fuzzy matching
    
    Example:
    Input: "President Wickremesinghe"
    Output: entity_master.id = 123 ("Ranil Wickremesinghe")
    """
    # Query entity_master for similar names
    # Use Levenshtein distance + type matching
    # If match score > 85%: return existing ID
    # Else: create new entity in master
```

---

### **Step 4: Topic Modeler with Trending Detection**

**File:** `layer2/services/topic_modeler.py`

```python
class TopicModeler:
    def __init__(self):
        self.vector_db = ChromaDB()  # For semantic search
    
    def extract_topics(self, article):
        """
        Extract topics and detect trends
        
        Returns:
        {
            "main_topic": "Currency Crisis",
            "sub_topics": ["exchange rates", "imports", "reserves"],
            "keywords": ["LKR", "depreciation", "forex"],
            "is_emerging": True,
            "related_topics": ["inflation", "economic slowdown"],
            "topic_evolution": "escalating"
        }
        """
        # Call LLM for topic extraction
        # Store topic embedding in ChromaDB
        # Query similar topics from history
        # Calculate topic velocity (mentions over time)
        # Determine if trending
        # Return topics with metadata
```

**Trending Detection:**
```python
def detect_trending_topics():
    """
    Identify topics with high velocity
    
    velocity = (mentions_today - mentions_yesterday) / mentions_yesterday
    
    If velocity > 50%: Mark as trending
    """
    # Query topic_trends table
    # Calculate velocity for each topic
    # Flag trending topics
    # Update is_trending column
```

---

### **Step 5: Multi-Source Validator**

**File:** `layer2/services/validator.py`

```python
class MultiSourceValidator:
    def validate_article(self, article):
        """
        Cross-validate with other sources
        
        Returns:
        {
            "confidence_score": 85,
            "supporting_articles": [123, 456, 789],
            "consensus_reached": True
        }
        """
        # Extract key claims from article (LLM)
        # Search for similar articles (last 48 hours)
        # Check if claims are confirmed by other sources
        # Calculate confidence:
        #   3+ sources = 80-100% confidence
        #   2 sources = 50-79% confidence
        #   1 source = 0-49% confidence
        # Store validation results
```

**Claim Extraction Prompt:**
```yaml
System: "Fact extraction specialist"

User: "Extract verifiable claims from this article:
       {content}
       
       List each factual claim with:
       - What is claimed
       - Who made the claim
       - Type (price_change, date, announcement, etc.)"

Output:
  [
    {
      "claim": "Fuel price increased by 20 LKR",
      "entity": "CPC",
      "type": "price_change"
    }
  ]
```

---

### **Step 6: Adaptive Indicator Calculator**

**File:** `layer2/services/adaptive_indicators.py`

```python
class AdaptiveIndicatorCalculator:
    def calculate_indicator(self, indicator_name, articles):
        """
        Calculate indicator with adaptive weights
        
        Flow:
        1. Get current context (LLM)
        2. LLM suggests weight adjustments
        3. Apply weights to article sentiments
        4. Calculate weighted average
        5. Check for anomalies
        6. Return indicator value + confidence
        """
        # Get articles for this indicator
        # Analyze context (elections coming? crisis?)
        # Ask LLM for weight recommendations
        # Calculate weighted average
        # Detect anomalies (outside 2 std dev)
        # Store with metadata
```

**Weight Advisory Prompt:**
```yaml
System: "Indicator calculation advisor"

User:
  Indicator: Political Stability Index
  
  Current articles (last 7 days):
  - 15 about elections
  - 8 about protests
  - 5 about policy changes
  
  Current weights:
  - Elections: 30%
  - Protests: 50%
  - Policy: 20%
  
  Recommend weight adjustments given context.

Output:
  {
    "recommended_weights": {
      "elections": 40,
      "protests": 45,
      "policy": 15
    },
    "reasoning": "Election in 2 weeks makes election news more impactful",
    "confidence": 85
  }
```

---

### **Step 7: Quality Scorer**

**File:** `layer2/services/quality_scorer.py`

```python
class QualityScorer:
    def calculate_quality(self, processed_article):
        """
        Calculate overall quality score (0-100)
        
        Components:
        - Classification quality (25%)
        - Sentiment quality (20%)
        - Entity quality (20%)
        - Validation quality (20%)
        - Completeness (15%)
        """
        scores = {
            "classification": self._classification_quality(article),
            "sentiment": self._sentiment_quality(article),
            "entity": self._entity_quality(article),
            "validation": self._validation_quality(article),
            "completeness": self._completeness_quality(article)
        }
        
        total = (
            scores["classification"] * 0.25 +
            scores["sentiment"] * 0.20 +
            scores["entity"] * 0.20 +
            scores["validation"] * 0.20 +
            scores["completeness"] * 0.15
        )
        
        # Assign quality band
        band = self._get_quality_band(total)
        
        return {
            "overall_quality": total,
            "quality_band": band,
            "component_scores": scores
        }
```

**Quality Bands:**
```
90-100: Excellent (use for critical decisions)
75-89:  Good (reliable)
60-74:  Fair (use with caution)
40-59:  Poor (needs review)
0-39:   Unreliable (exclude)
```

---

## INTEGRATION WITH EXISTING SYSTEM

### **Parallel Processing Strategy:**

```python
# layer2/pipeline.py

class Layer2Pipeline:
    def __init__(self, use_enhanced=True):
        self.use_enhanced = use_enhanced
        self.basic_pipeline = BasicPipeline()
        self.enhanced_pipeline = EnhancedPipeline()
    
    def process_article(self, article):
        if self.use_enhanced:
            # Use enhanced AI/LLM pipeline
            result = self.enhanced_pipeline.process(article)
            
            # Fallback to basic if enhanced fails
            if result is None:
                result = self.basic_pipeline.process(article)
        else:
            # Use basic pipeline
            result = self.basic_pipeline.process(article)
        
        return result
```

### **Feature Flags (config.yaml):**

```yaml
layer2:
  enhancements:
    llm_classification: true
    advanced_sentiment: true
    smart_ner: true
    topic_modeling: true
    multi_source_validation: true
    adaptive_indicators: true
    quality_scoring: true
  
  llm:
    provider: groq
    model: llama-3.1-70b-versatile
    fallback_provider: together
    fallback_to_basic: true
  
  performance:
    enable_caching: true
    cache_ttl_hours: 24
    batch_size: 10
    selective_llm_usage: true
```

### **Backward Compatibility:**

```python
# Ensure Layer 3 still works
class Layer2Adapter:
    """Adapter to maintain compatibility with Layer 3"""
    
    def get_indicators(self):
        """
        Return indicators in exact format Layer 3 expects
        Even if internal structure changed
        """
        indicators = self.enhanced_calculator.get_all_indicators()
        
        # Transform to old format
        return {
            "political_stability": indicators["political_stability"]["value"],
            "economic_health": indicators["economic_health"]["value"],
            # ... all 20 indicators
        }
```

---

## PERFORMANCE OPTIMIZATION

### **1. Caching Strategy:**

```python
# Redis caching
def classify_with_cache(article):
    # Create cache key
    cache_key = f"classify:{article_hash}"
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Not in cache - call LLM
    result = llm_classify(article)
    
    # Cache for 24 hours
    redis_client.setex(cache_key, 86400, json.dumps(result))
    
    return result
```

**Expected cache hit rate: 60-70%**

### **2. Selective LLM Usage:**

```python
def should_use_llm(article):
    """Decide if LLM needed or basic is enough"""
    
    # Use LLM for:
    if article['length'] > 500:  # Complex articles
        return True
    if article['source'] in CRITICAL_SOURCES:  # Important sources
        return True
    if basic_classifier_confidence < 0.7:  # Ambiguous content
        return True
    
    # Use basic for:
    return False  # Short, clear articles
```

**Expected LLM reduction: 30-40%**

### **3. Batch Processing:**

```python
def process_articles_batch(articles):
    """Process multiple articles in one LLM call"""
    
    # Group articles into batches of 10
    batches = [articles[i:i+10] for i in range(0, len(articles), 10)]
    
    for batch in batches:
        # Single LLM call for entire batch
        results = llm_classify_batch(batch)
        
        # Store results
        for article, result in zip(batch, results):
            store_classification(article, result)
```

---

## TESTING & VALIDATION

### **Quality Validation:**

```python
def validate_enhancements():
    """
    Test enhanced system against baseline
    """
    # Select 100 random articles
    test_articles = sample_articles(100)
    
    # Process with both systems
    basic_results = [basic_classify(a) for a in test_articles]
    enhanced_results = [enhanced_classify(a) for a in test_articles]
    
    # Get human annotations
    human_labels = get_human_annotations(test_articles)
    
    # Calculate accuracy
    basic_accuracy = accuracy(basic_results, human_labels)
    enhanced_accuracy = accuracy(enhanced_results, human_labels)
    
    print(f"Basic: {basic_accuracy}%")
    print(f"Enhanced: {enhanced_accuracy}%")
    print(f"Improvement: {enhanced_accuracy - basic_accuracy}%")
```

### **Performance Monitoring:**

```python
# Track metrics
metrics = {
    "processing_time_avg": [],
    "llm_calls_per_day": 0,
    "cache_hit_rate": 0,
    "quality_score_avg": [],
    "accuracy_samples": []
}

# Log to database
def log_metrics():
    cursor.execute("""
        INSERT INTO layer2_metrics (date, processing_time, llm_calls, cache_hits, quality_avg)
        VALUES (%s, %s, %s, %s, %s)
    """, (today, avg_time, llm_count, cache_rate, quality_avg))
```

---

## SUCCESS CRITERIA

```yaml
Accuracy Goals:
  ✅ Classification: 90%+ (vs 75% baseline)
  ✅ Sentiment: 85%+ (vs 70% baseline)
  ✅ Entity extraction: 90%+ recall (vs 80% baseline)

Performance Goals:
  ✅ Processing: <3 seconds/article (vs 5s baseline)
  ✅ LLM cost: $0/month (Groq free tier)
  ✅ Cache hit rate: 60%+

Quality Goals:
  ✅ 70%+ articles with quality score >= 75
  ✅ Indicator reliability: 75%+ correlation with events
  ✅ User satisfaction: 4.5/5 stars
```

---

## 8-WEEK IMPLEMENTATION ROADMAP

**Week 1-2: Setup & Foundation**
- ✅ Set up Groq API
- ✅ Install LangChain, ChromaDB
- ✅ Create database schemas
- ✅ Implement classification service
- ✅ Test on 100 articles

**Week 3-4: Core Enhancements**
- ✅ Advanced sentiment
- ✅ Smart entity extraction
- ✅ Topic modeling
- ✅ Multi-source validation
- ✅ Performance benchmarks

**Week 5-6: Integration**
- ✅ Adaptive indicators
- ✅ Quality scoring
- ✅ Compatibility layer
- ✅ Parallel processing setup
- ✅ A/B testing (20% traffic)

**Week 7-8: Optimization & Rollout**
- ✅ Optimize caching
- ✅ Batch processing
- ✅ Full migration (100%)
- ✅ Monitor quality metrics
- ✅ Documentation
- ✅ Team training

---

**This comprehensive plan provides all instructions needed to enhance Layer 2 with AI/LLM while maintaining compatibility, improving accuracy from 75% to 90%+, and keeping costs at $0 with Groq's free tier.**
