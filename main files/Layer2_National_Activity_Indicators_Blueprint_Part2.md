# LAYER 2: NATIONAL ACTIVITY INDICATOR ENGINE
## Comprehensive Architectural Blueprint & Implementation Plan - PART 2

---

## TABLE OF CONTENTS - PART 2

1. [Pass 2: ML Classification Pipeline](#ml-classification)
2. [Pass 3: Entity & Numeric Extraction](#entity-extraction)
3. [Indicator Calculation Methodologies](#calculation-methods)
4. [Weighting & Scoring Systems](#weighting-systems)
5. [Composite Indicators & Dependencies](#composite-indicators)
6. [Trend Analysis & Forecasting](#trend-analysis)
7. [Anomaly Detection](#anomaly-detection)
8. [Narrative Generation](#narrative-generation)
9. [Iteration 1 Implementation Checklist](#iteration-1-checklist)
10. [Iteration 2 Advanced Features](#iteration-2-features)
11. [Integration with Layer 3](#integration-layer3)
12. [Testing Strategy](#testing-strategy)
13. [Performance & Optimization](#performance-optimization)

---

## PASS 2: ML CLASSIFICATION PIPELINE {#ml-classification}

### 2.5 MACHINE LEARNING BASED INDICATOR ASSIGNMENT

#### ML Strategy Overview

**Why ML After Rule-Based?**
- **Nuance**: Captures semantic relationships keywords miss
- **Context**: Understands article meaning, not just word presence
- **Multi-label**: One article can contribute to multiple indicators
- **Learning**: Improves over time with new training data

**ML Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│          ML CLASSIFICATION SYSTEM                        │
└─────────────────────────────────────────────────────────┘

Article Text (preprocessed)
        ↓
┌──────────────────┐
│  Text Vectorizer │
│  - TF-IDF or     │
│  - BERT embeddings│
└──────────────────┘
        ↓
┌──────────────────┐
│  Multi-Label     │
│  Classifier      │
│  - Trained on    │
│    labeled data  │
└──────────────────┘
        ↓
Indicator Probabilities
[{indicator_id: 1, prob: 0.85},
 {indicator_id: 15, prob: 0.72},
 {indicator_id: 23, prob: 0.45}]
        ↓
Filter by threshold (0.5)
        ↓
Final Indicator Assignments
```

#### Training Data Preparation

**Phase 1: Manual Labeling (Bootstrap)**

**Approach:**
```
Create training dataset:
├── Select 1,000 diverse articles
├── Manually label each with relevant indicators
├── Multiple labels per article allowed
├── Record confidence for each label
└── Store in training_data table
```

**Labeling Interface Requirements:**
```
Article Display:
├── Title and full text
├── Extracted keywords highlighted
├── Source and credibility shown

Labeling Tools:
├── Checkbox list of all indicators
├── Relevance slider (0-100%) per indicator
├── Quick-select for common patterns
├── Notes field for edge cases
└── Bulk labeling for similar articles

Output Format:
{
    "article_id": "ada_derana_001234",
    "labels": [
        {"indicator_id": 1, "relevance": 0.9, "primary": true},
        {"indicator_id": 15, "relevance": 0.6, "primary": false}
    ],
    "labeled_by": "user_id",
    "labeled_at": "timestamp"
}
```

**Phase 2: Semi-Automated Labeling**

**Active Learning Approach:**
```
1. Train initial model on 1,000 labeled articles
2. Use model to predict labels for 10,000 unlabeled articles
3. Select most uncertain predictions for human review
4. Human verifies/corrects these predictions
5. Add verified labels to training set
6. Retrain model
7. Repeat cycle
```

**Benefits:**
- Reduces manual labeling effort by 80%
- Focuses human attention on difficult cases
- Rapidly expands training dataset

**Phase 3: Weak Supervision (Advanced)**

**Use Rule-Based as Weak Labels:**
```
For articles without manual labels:
├── If rule-based confidence > 0.8:
│   └── Use as training label (but with lower weight)
├── If multiple rule-based matches agree:
│   └── Higher confidence weak label
└── Weak labels get 0.5x weight in training
```

#### Model Architecture Options

**Option 1: Classical ML (Recommended for Iteration 1)**

**Algorithm: Multi-Label Random Forest or XGBoost**

```
Advantages:
├── Fast training and inference
├── Works well with limited data (1,000+ samples)
├── Interpretable (can see feature importance)
├── Low computational requirements
└── Good baseline performance

Disadvantages:
├── Requires manual feature engineering
├── Limited understanding of context
└── May miss subtle semantic patterns
```

**Implementation Approach:**

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from xgboost import XGBClassifier

class MLIndicatorClassifier:
    
    def __init__(self):
        # Text vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=2,
            max_df=0.8,
            stop_words='english'
        )
        
        # Multi-label classifier
        self.classifier = MultiOutputClassifier(
            XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                objective='binary:logistic'
            )
        )
        
        self.indicator_mapping = self._load_indicator_mapping()
        self.is_trained = False
    
    def train(self, training_data):
        """Train on labeled articles"""
        
        # Prepare features
        texts = [article['content']['body'] for article in training_data]
        X = self.vectorizer.fit_transform(texts)
        
        # Prepare labels (multi-label binary matrix)
        y = self._create_label_matrix(training_data)
        
        # Train
        self.classifier.fit(X, y)
        self.is_trained = True
        
        # Evaluate
        scores = self._cross_validate(X, y)
        logger.info(f"Training complete. CV scores: {scores}")
    
    def predict(self, article):
        """Predict indicators for new article"""
        
        if not self.is_trained:
            raise Exception("Model not trained")
        
        # Vectorize
        text = article['content']['body']
        X = self.vectorizer.transform([text])
        
        # Predict probabilities
        probabilities = self.classifier.predict_proba(X)[0]
        
        # Format results
        predictions = []
        for idx, indicator_id in enumerate(self.indicator_mapping):
            prob = probabilities[idx][1]  # Probability of class 1
            
            if prob >= ML_CONFIDENCE_THRESHOLD:
                predictions.append({
                    'indicator_id': indicator_id,
                    'confidence': float(prob),
                    'method': 'ml_classification'
                })
        
        return sorted(predictions, key=lambda x: x['confidence'], reverse=True)
    
    def _create_label_matrix(self, training_data):
        """Convert article labels to binary matrix"""
        
        n_samples = len(training_data)
        n_indicators = len(self.indicator_mapping)
        y = np.zeros((n_samples, n_indicators))
        
        for i, article in enumerate(training_data):
            for label in article['labels']:
                indicator_idx = self.indicator_mapping.index(label['indicator_id'])
                y[i, indicator_idx] = label['relevance']  # Can use relevance as weight
        
        return y
    
    def _cross_validate(self, X, y, cv=5):
        """Evaluate model performance"""
        from sklearn.model_selection import cross_val_score
        from sklearn.metrics import f1_score, make_scorer
        
        # Use F1 score for each indicator
        scorer = make_scorer(f1_score, average='samples')
        scores = cross_val_score(self.classifier, X, y, cv=cv, scoring=scorer)
        
        return {
            'mean_f1': np.mean(scores),
            'std_f1': np.std(scores)
        }
```

**Option 2: Deep Learning (Iteration 2+)**

**Algorithm: Fine-tuned BERT for Multi-Label Classification**

```
Advantages:
├── Superior semantic understanding
├── Captures context and nuance
├── Transfer learning from pre-trained models
├── Better handling of rare indicators
└── Can process multiple languages (multilingual BERT)

Disadvantages:
├── Requires more training data (5,000+ samples ideal)
├── Computationally expensive (GPU recommended)
├── Longer training time
├── Less interpretable
└── Higher deployment complexity
```

**Implementation Approach:**

```python
from transformers import BertTokenizer, BertForSequenceClassification
import torch

class BERTIndicatorClassifier:
    
    def __init__(self, model_name='bert-base-uncased'):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=len(INDICATOR_LIST),  # Multi-label
            problem_type="multi_label_classification"
        )
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def train(self, training_data, epochs=3, batch_size=16):
        """Fine-tune BERT on indicator classification"""
        
        # Prepare dataset
        train_dataset = self._prepare_dataset(training_data)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Optimizer
        optimizer = AdamW(self.model.parameters(), lr=2e-5)
        
        # Training loop
        self.model.train()
        for epoch in range(epochs):
            for batch in train_loader:
                # Move to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            logger.info(f"Epoch {epoch+1} complete, loss: {loss.item()}")
    
    def predict(self, article):
        """Predict indicators using BERT"""
        
        self.model.eval()
        
        # Tokenize
        text = article['content']['title'] + " " + article['content']['body']
        encoding = self.tokenizer(
            text,
            max_length=512,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.sigmoid(logits)[0]  # Multi-label
        
        # Format results
        predictions = []
        for idx, prob in enumerate(probabilities):
            if prob >= ML_CONFIDENCE_THRESHOLD:
                predictions.append({
                    'indicator_id': INDICATOR_LIST[idx],
                    'confidence': float(prob),
                    'method': 'bert_classification'
                })
        
        return sorted(predictions, key=lambda x: x['confidence'], reverse=True)
```

#### Combining Rule-Based + ML Results

**Ensemble Strategy:**

```python
class HybridIndicatorAssigner:
    
    def __init__(self):
        self.rule_based = RuleBasedIndicatorAssigner()
        self.ml_classifier = MLIndicatorClassifier()
    
    def assign_indicators(self, article):
        """Combine rule-based and ML predictions"""
        
        # Get both predictions
        rule_predictions = self.rule_based.assign_indicators(article)
        ml_predictions = self.ml_classifier.predict(article)
        
        # Combine
        combined = self._merge_predictions(rule_predictions, ml_predictions)
        
        # Apply business logic
        final = self._apply_business_rules(combined, article)
        
        return final
    
    def _merge_predictions(self, rule_preds, ml_preds):
        """Merge and weight predictions from both methods"""
        
        indicator_scores = {}
        
        # Add rule-based (weight: 0.4)
        for pred in rule_preds:
            ind_id = pred['indicator_id']
            indicator_scores[ind_id] = {
                'rule_confidence': pred['confidence'] * 0.4,
                'ml_confidence': 0.0,
                'methods': ['rule_based'],
                'matched_keywords': pred.get('matched_keywords', [])
            }
        
        # Add ML predictions (weight: 0.6)
        for pred in ml_preds:
            ind_id = pred['indicator_id']
            if ind_id in indicator_scores:
                indicator_scores[ind_id]['ml_confidence'] = pred['confidence'] * 0.6
                indicator_scores[ind_id]['methods'].append('ml_classification')
            else:
                indicator_scores[ind_id] = {
                    'rule_confidence': 0.0,
                    'ml_confidence': pred['confidence'] * 0.6,
                    'methods': ['ml_classification'],
                    'matched_keywords': []
                }
        
        # Calculate final confidence
        results = []
        for ind_id, scores in indicator_scores.items():
            final_confidence = scores['rule_confidence'] + scores['ml_confidence']
            
            # Boost if both methods agree
            if len(scores['methods']) == 2:
                final_confidence *= 1.2  # 20% boost for agreement
                final_confidence = min(final_confidence, 1.0)
            
            results.append({
                'indicator_id': ind_id,
                'confidence': final_confidence,
                'methods': scores['methods'],
                'rule_confidence': scores['rule_confidence'],
                'ml_confidence': scores['ml_confidence'],
                'matched_keywords': scores['matched_keywords']
            })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)
    
    def _apply_business_rules(self, predictions, article):
        """Apply domain-specific logic"""
        
        # Filter low confidence
        filtered = [p for p in predictions if p['confidence'] >= FINAL_THRESHOLD]
        
        # Limit to top N indicators per article (avoid over-assignment)
        filtered = filtered[:MAX_INDICATORS_PER_ARTICLE]
        
        # Check for mutual exclusions
        # (e.g., "Positive Economic Sentiment" and "Economic Crisis" shouldn't both be high)
        filtered = self._resolve_conflicts(filtered)
        
        return filtered
    
    def _resolve_conflicts(self, predictions):
        """Resolve mutually exclusive indicators"""
        
        # Load conflict rules from database
        conflicts = self._load_conflict_rules()
        
        for conflict in conflicts:
            ind_a, ind_b = conflict['indicator_a'], conflict['indicator_b']
            
            # Check if both present
            pred_a = next((p for p in predictions if p['indicator_id'] == ind_a), None)
            pred_b = next((p for p in predictions if p['indicator_id'] == ind_b), None)
            
            if pred_a and pred_b:
                # Keep the one with higher confidence
                if pred_a['confidence'] > pred_b['confidence']:
                    predictions.remove(pred_b)
                else:
                    predictions.remove(pred_a)
        
        return predictions
```

---

## PASS 3: ENTITY & NUMERIC EXTRACTION {#entity-extraction}

### 2.6 EXTRACTING STRUCTURED DATA FROM ARTICLES

#### Entity Extraction Pipeline

**Purpose**: Extract specific pieces of information that enrich indicators

**What to Extract:**

```
Named Entities:
├── LOCATIONS: Countries, cities, regions, districts
├── ORGANIZATIONS: Companies, government bodies, institutions
├── PERSONS: Politicians, business leaders, officials
├── DATES: Event dates, deadlines, time periods
└── AMOUNTS: Money, percentages, quantities

Numeric Values:
├── Financial figures (GDP, revenue, losses)
├── Statistics (growth rates, percentages, counts)
├── Measurements (distances, weights, volumes)
└── Scores/Ratings
```

**Implementation:**

```python
import spacy
import re
from dateutil import parser as date_parser

class EntityExtractor:
    
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Currency patterns
        self.currency_pattern = re.compile(
            r'(?:Rs\.?|LKR|USD|\$|€|¥)\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|mn|bn|M|B)?',
            re.IGNORECASE
        )
        
        # Percentage pattern
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
        
        # Extract using spaCy NER
        for ent in doc.ents:
            if ent.label_ == 'GPE' or ent.label_ == 'LOC':
                entities['locations'].append({
                    'text': ent.text,
                    'type': 'location',
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            elif ent.label_ == 'ORG':
                entities['organizations'].append({
                    'text': ent.text,
                    'type': 'organization',
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            elif ent.label_ == 'PERSON':
                entities['persons'].append({
                    'text': ent.text,
                    'type': 'person',
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            elif ent.label_ == 'DATE':
                date_obj = self._parse_date(ent.text)
                if date_obj:
                    entities['dates'].append({
                        'text': ent.text,
                        'parsed': date_obj.isoformat(),
                        'type': 'date'
                    })
            
            elif ent.label_ == 'MONEY':
                amount = self._parse_amount(ent.text)
                if amount:
                    entities['amounts'].append(amount)
        
        # Extract using regex patterns
        amounts = self._extract_amounts_regex(text)
        entities['amounts'].extend(amounts)
        
        # Deduplicate
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _parse_amount(self, text):
        """Parse monetary amount"""
        
        match = self.currency_pattern.search(text)
        if match:
            value = float(match.group(1).replace(',', ''))
            multiplier_text = match.group(2)
            
            # Apply multiplier
            if multiplier_text:
                multipliers = {
                    'million': 1e6, 'mn': 1e6, 'M': 1e6,
                    'billion': 1e9, 'bn': 1e9, 'B': 1e9
                }
                value *= multipliers.get(multiplier_text.lower(), 1)
            
            return {
                'text': text,
                'value': value,
                'type': 'monetary',
                'currency': self._extract_currency(text)
            }
        
        return None
    
    def _extract_amounts_regex(self, text):
        """Extract amounts using regex patterns"""
        
        amounts = []
        
        # Currency amounts
        for match in self.currency_pattern.finditer(text):
            amount = self._parse_amount(match.group(0))
            if amount:
                amounts.append(amount)
        
        # Percentages
        for match in self.percentage_pattern.finditer(text):
            amounts.append({
                'text': match.group(0),
                'value': float(match.group(1)),
                'type': 'percentage'
            })
        
        return amounts
    
    def _parse_date(self, date_text):
        """Parse date string to datetime object"""
        try:
            return date_parser.parse(date_text, fuzzy=True)
        except:
            return None
    
    def _extract_currency(self, text):
        """Determine currency from text"""
        if 'Rs' in text or 'LKR' in text:
            return 'LKR'
        elif '$' in text or 'USD' in text:
            return 'USD'
        elif '€' in text:
            return 'EUR'
        return 'unknown'
    
    def _deduplicate_entities(self, entities):
        """Remove duplicate entities"""
        for entity_type in entities:
            unique = []
            seen = set()
            for entity in entities[entity_type]:
                key = entity['text'].lower()
                if key not in seen:
                    unique.append(entity)
                    seen.add(key)
            entities[entity_type] = unique
        
        return entities
```

#### Using Extracted Entities in Indicators

**Example: Currency Stability Indicator**

```python
def calculate_currency_stability_indicator(articles, entities_list):
    """
    Use extracted currency mentions to gauge stability
    """
    
    currency_mentions = []
    negative_sentiment_count = 0
    
    for article, entities in zip(articles, entities_list):
        # Find currency-related amounts
        for amount in entities['amounts']:
            if amount['currency'] == 'LKR':
                currency_mentions.append({
                    'value': amount['value'],
                    'article_id': article['article_id'],
                    'sentiment': article.get('sentiment_score', 0)
                })
                
                if article.get('sentiment_score', 0) < 0:
                    negative_sentiment_count += 1
    
    # Calculate instability score
    if len(currency_mentions) > 0:
        negative_ratio = negative_sentiment_count / len(currency_mentions)
        instability_score = negative_ratio * 100
    else:
        instability_score = 50  # Neutral if no data
    
    return {
        'value': instability_score,
        'mentions_count': len(currency_mentions),
        'negative_mentions': negative_sentiment_count
    }
```

**Example: Geographic Concentration**

```python
def calculate_geographic_concentration(articles, entities_list):
    """
    Identify which regions are mentioned most frequently
    """
    
    location_counts = {}
    
    for article, entities in zip(articles, entities_list):
        for location in entities['locations']:
            loc_name = location['text']
            location_counts[loc_name] = location_counts.get(loc_name, 0) + 1
    
    # Sort by frequency
    sorted_locations = sorted(
        location_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return {
        'top_locations': sorted_locations[:10],
        'geographic_diversity': len(location_counts),
        'concentration_index': sorted_locations[0][1] / sum(location_counts.values()) if sorted_locations else 0
    }
```

---

## INDICATOR CALCULATION METHODOLOGIES {#calculation-methods}

### 2.7 COMPUTING INDICATOR VALUES

#### Calculation Type 1: Frequency-Based Indicators

**Purpose**: Count occurrences of events or mentions

**Example: Protest Frequency Index**

```python
def calculate_protest_frequency_index(articles, time_window_days=7):
    """
    Count protest-related articles over time window
    Compare to historical baseline
    """
    
    # Filter articles assigned to protest indicator
    protest_articles = [
        a for a in articles 
        if 'protest_indicator' in a['assigned_indicators']
    ]
    
    current_count = len(protest_articles)
    
    # Get historical average from database
    historical_avg = get_historical_average(
        indicator_id='protest_frequency',
        window_days=time_window_days,
        lookback_days=90
    )
    
    # Calculate index (100 = baseline)
    if historical_avg > 0:
        index_value = (current_count / historical_avg) * 100
    else:
        index_value = 100  # No historical data
    
    # Determine severity level
    if index_value >= 200:
        severity = "Critical"
    elif index_value >= 150:
        severity = "High"
    elif index_value >= 100:
        severity = "Elevated"
    else:
        severity = "Normal"
    
    return {
        'value': index_value,
        'raw_count': current_count,
        'historical_avg': historical_avg,
        'severity': severity,
        'contributing_articles': len(protest_articles),
        'confidence': calculate_confidence(current_count)
    }

def calculate_confidence(data_points):
    """
    Confidence increases with more data points
    """
    # Sigmoid function
    return min(1.0, data_points / 20.0)
```

#### Calculation Type 2: Sentiment-Based Indicators

**Purpose**: Aggregate sentiment across relevant articles

**Example: Consumer Confidence Proxy**

```python
def calculate_consumer_confidence_proxy(articles):
    """
    Aggregate sentiment from consumer-related articles
    """
    
    # Filter for consumer/economic articles
    consumer_articles = [
        a for a in articles
        if 'consumer_behavior' in a['assigned_indicators'] or
           'economic_sentiment' in a['assigned_indicators']
    ]
    
    if not consumer_articles:
        return None
    
    # Calculate weighted sentiment
    total_weight = 0
    weighted_sentiment_sum = 0
    
    for article in consumer_articles:
        # Get sentiment score from article
        sentiment = article.get('sentiment_score', 0)  # -1 to +1
        
        # Calculate weight based on credibility and recency
        credibility = article['quality']['credibility_score']
        recency_weight = calculate_recency_weight(article['metadata']['publish_timestamp'])
        
        weight = credibility * recency_weight
        
        weighted_sentiment_sum += sentiment * weight
        total_weight += weight
    
    # Calculate final score
    if total_weight > 0:
        avg_sentiment = weighted_sentiment_sum / total_weight
    else:
        avg_sentiment = 0
    
    # Convert from [-1, 1] to [0, 100] scale
    confidence_score = ((avg_sentiment + 1) / 2) * 100
    
    # Classify
    if confidence_score >= 70:
        classification = "Optimistic"
    elif confidence_score >= 50:
        classification = "Neutral"
    elif confidence_score >= 30:
        classification = "Pessimistic"
    else:
        classification = "Very Negative"
    
    return {
        'value': confidence_score,
        'classification': classification,
        'avg_sentiment': avg_sentiment,
        'article_count': len(consumer_articles),
        'confidence': calculate_confidence(len(consumer_articles))
    }

def calculate_recency_weight(publish_timestamp):
    """
    More recent articles weighted higher
    """
    from datetime import datetime, timedelta
    
    now = datetime.now()
    age = now - publish_timestamp
    
    # Exponential decay
    # Articles from today: 1.0
    # 1 day old: 0.8
    # 3 days old: 0.5
    # 7 days old: 0.2
    
    decay_rate = 0.2  # decay per day
    weight = math.exp(-decay_rate * age.days)
    
    return max(weight, 0.1)  # Minimum weight 0.1
```

#### Calculation Type 3: Numeric Extraction Indicators

**Purpose**: Extract and aggregate specific numeric values

**Example: Inflation Pressure Index**

```python
def calculate_inflation_pressure_index(articles, entities_list):
    """
    Extract price increase mentions and amounts
    """
    
    price_increases = []
    inflation_keywords = ['inflation', 'price increase', 'expensive', 'costly']
    
    for article, entities in zip(articles, entities_list):
        # Check if article mentions inflation/prices
        article_text = article['content']['body'].lower()
        
        if any(keyword in article_text for keyword in inflation_keywords):
            # Extract percentages (likely price increase percentages)
            for amount in entities['amounts']:
                if amount['type'] == 'percentage':
                    price_increases.append({
                        'percentage': amount['value'],
                        'article_id': article['article_id'],
                        'credibility': article['quality']['credibility_score']
                    })
    
    if not price_increases:
        return {
            'value': 0,
            'interpretation': "No significant inflation signals detected"
        }
    
    # Calculate weighted average of price increases
    total_weight = 0
    weighted_sum = 0
    
    for increase in price_increases:
        weight = increase['credibility']
        weighted_sum += increase['percentage'] * weight
        total_weight += weight
    
    avg_increase = weighted_sum / total_weight if total_weight > 0 else 0
    
    # Classify pressure level
    if avg_increase >= 15:
        pressure_level = "Extreme"
    elif avg_increase >= 10:
        pressure_level = "High"
    elif avg_increase >= 5:
        pressure_level = "Moderate"
    else:
        pressure_level = "Low"
    
    return {
        'value': avg_increase,
        'pressure_level': pressure_level,
        'mentions_count': len(price_increases),
        'confidence': calculate_confidence(len(price_increases))
    }
```

#### Calculation Type 4: Ratio-Based Indicators

**Purpose**: Compare two related metrics

**Example: Economic Optimism Ratio**

```python
def calculate_economic_optimism_ratio(articles):
    """
    Ratio of positive to negative economic news
    """
    
    economic_articles = [
        a for a in articles
        if any(ind.startswith('ECONOMIC') for ind in a['assigned_indicators'])
    ]
    
    positive_count = sum(
        1 for a in economic_articles 
        if a.get('sentiment_score', 0) > 0.2
    )
    
    negative_count = sum(
        1 for a in economic_articles 
        if a.get('sentiment_score', 0) < -0.2
    )
    
    neutral_count = len(economic_articles) - positive_count - negative_count
    
    # Calculate ratio
    if negative_count > 0:
        optimism_ratio = positive_count / negative_count
    else:
        optimism_ratio = positive_count  # All positive, no negatives
    
    # Normalize to 0-100 scale
    # Ratio of 1.0 (equal positive/negative) = 50
    # Ratio of 2.0 (2x positive) = 67
    # Ratio of 0.5 (2x negative) = 33
    
    normalized_score = (optimism_ratio / (1 + optimism_ratio)) * 100
    
    return {
        'value': normalized_score,
        'ratio': optimism_ratio,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'total_articles': len(economic_articles)
    }
```

---

## WEIGHTING & SCORING SYSTEMS {#weighting-systems}

### 2.8 MULTI-FACTOR WEIGHTING

**The Weighting Formula:**

```
Final_Impact_Score = 
    Recency_Weight × 
    Severity_Weight × 
    Source_Credibility_Weight × 
    Volume_Weight ×
    Base_Value
```

#### Factor 1: Recency Weight

```python
def calculate_recency_weight(publish_timestamp):
    """
    Exponential decay based on age
    """
    from datetime import datetime
    
    age_hours = (datetime.now() - publish_timestamp).total_seconds() / 3600
    
    if age_hours < 6:
        return 1.0      # Last 6 hours: full weight
    elif age_hours < 24:
        return 0.9      # Last day: 90%
    elif age_hours < 72:
        return 0.7      # Last 3 days: 70%
    elif age_hours < 168:
        return 0.5      # Last week: 50%
    else:
        return 0.3      # Older: 30%
```

#### Factor 2: Severity Weight

```python
def calculate_severity_weight(indicator_type, article_content):
    """
    Determine how severe/important the event is
    """
    
    # Crisis keywords indicate high severity
    crisis_keywords = ['crisis', 'emergency', 'critical', 'urgent', 'breakdown', 'collapse']
    
    severity_score = 0.5  # Base severity
    
    article_text = article_content.lower()
    
    # Check for crisis language
    crisis_mentions = sum(1 for keyword in crisis_keywords if keyword in article_text)
    if crisis_mentions > 0:
        severity_score += 0.3
    
    # Check for scale indicators
    scale_keywords = ['nationwide', 'country-wide', 'all provinces', 'widespread']
    if any(keyword in article_text for keyword in scale_keywords):
        severity_score += 0.2
    
    # Check for duration indicators
    duration_keywords = ['indefinite', 'extended', 'ongoing', 'continues']
    if any(keyword in article_text for keyword in duration_keywords):
        severity_score += 0.1
    
    # Cap at 1.0
    return min(severity_score, 1.0)
```

#### Factor 3: Source Credibility Weight

```python
def calculate_source_credibility_weight(article):
    """
    Use source credibility from Layer 1
    """
    base_credibility = article['quality']['credibility_score']
    
    # Boost for government sources on policy indicators
    if article['metadata']['source'] in GOVERNMENT_SOURCES:
        if article_is_about_policy(article):
            base_credibility *= 1.2
    
    # Reduce for social media
    if article['metadata']['source_type'] == 'social':
        base_credibility *= 0.7
    
    return min(base_credibility, 1.0)
```

#### Factor 4: Volume Weight

```python
def calculate_volume_weight(article_count):
    """
    More articles = higher confidence, but with diminishing returns
    """
    # Logarithmic scaling
    # 1 article: 0.3
    # 10 articles: 0.7
    # 50 articles: 0.9
    # 100+ articles: 1.0
    
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
```

#### Applying Weights to Indicator Calculation

```python
def calculate_weighted_indicator(articles, indicator_definition):
    """
    Apply multi-factor weighting to indicator calculation
    """
    
    total_weighted_score = 0
    total_weight = 0
    
    for article in articles:
        # Base contribution (e.g., sentiment score, or 1 for frequency)
        if indicator_definition['calculation_type'] == 'sentiment':
            base_value = article.get('sentiment_score', 0)
        else:
            base_value = 1  # For frequency counting
        
        # Calculate all weights
        recency = calculate_recency_weight(article['metadata']['publish_timestamp'])
        severity = calculate_severity_weight(indicator_definition['type'], article['content']['body'])
        credibility = calculate_source_credibility_weight(article)
        
        # Combined weight
        combined_weight = recency * severity * credibility
        
        # Accumulate
        total_weighted_score += base_value * combined_weight
        total_weight += combined_weight
    
    # Volume weight (based on article count)
    volume = calculate_volume_weight(len(articles))
    
    # Final calculation
    if total_weight > 0:
        weighted_avg = total_weighted_score / total_weight
        final_score = weighted_avg * volume
    else:
        final_score = 0
    
    return {
        'value': final_score,
        'contributing_articles': len(articles),
        'average_weight': total_weight / len(articles) if articles else 0,
        'volume_confidence': volume
    }
```

---

## COMPOSITE INDICATORS & DEPENDENCIES {#composite-indicators}

### 2.9 BUILDING COMPLEX INDICATORS FROM SIMPLE ONES

#### Composite Indicator Architecture

**Concept**: Some indicators are calculated from other indicators

**Example: Economic Health Index**

```python
def calculate_economic_health_index():
    """
    Composite of multiple economic sub-indicators
    """
    
    # Get component indicator values
    consumer_confidence = get_indicator_value('consumer_confidence_proxy')
    business_activity = get_indicator_value('business_activity_index')
    supply_chain = get_indicator_value('supply_chain_health')
    currency_sentiment = get_indicator_value('currency_stability')
    inflation_pressure = get_indicator_value('inflation_pressure_index')
    
    # Define weights (must sum to 1.0)
    weights = {
        'consumer_confidence': 0.30,
        'business_activity': 0.25,
        'supply_chain': 0.20,
        'currency_sentiment': 0.15,
        'inflation_pressure': 0.10
    }
    
    # Calculate weighted average
    # Note: Invert inflation (high inflation = bad health)
    economic_health = (
        consumer_confidence * weights['consumer_confidence'] +
        business_activity * weights['business_activity'] +
        supply_chain * weights['supply_chain'] +
        currency_sentiment * weights['currency_sentiment'] +
        (100 - inflation_pressure) * weights['inflation_pressure']
    )
    
    # Classify
    if economic_health >= 70:
        classification = "Strong"
    elif economic_health >= 50:
        classification = "Moderate"
    elif economic_health >= 30:
        classification = "Weak"
    else:
        classification = "Critical"
    
    return {
        'value': economic_health,
        'classification': classification,
        'components': {
            'consumer_confidence': consumer_confidence,
            'business_activity': business_activity,
            'supply_chain': supply_chain,
            'currency_sentiment': currency_sentiment,
            'inflation_pressure': inflation_pressure
        },
        'weights': weights
    }
```

#### Dependency Mapping

**Tracking Cause-Effect Relationships**

```python
class IndicatorDependencyEngine:
    
    def __init__(self):
        self.dependencies = self._load_dependencies()
    
    def _load_dependencies(self):
        """
        Load indicator dependencies from database
        
        Example dependency:
        {
            'parent': 'economic_health_index',
            'child': 'consumer_confidence_proxy',
            'relationship': 'component',
            'weight': 0.30
        }
        
        {
            'parent': 'transport_disruption',
            'child': 'fuel_shortage_index',
            'relationship': 'causes',
            'time_lag_hours': 48,
            'correlation': 0.85
        }
        """
        return query_database("SELECT * FROM indicator_dependencies WHERE is_active = true")
    
    def get_affected_indicators(self, indicator_id):
        """
        Find which indicators this one affects
        """
        affected = []
        
        for dep in self.dependencies:
            if dep['child'] == indicator_id and dep['relationship'] in ['causes', 'leads']:
                affected.append({
                    'indicator_id': dep['parent'],
                    'relationship': dep['relationship'],
                    'time_lag_hours': dep.get('time_lag_hours', 0),
                    'strength': dep.get('correlation', 0.5)
                })
        
        return affected
    
    def predict_secondary_effects(self, indicator_id, current_value, change_magnitude):
        """
        Predict how changes in this indicator affect others
        """
        
        affected = self.get_affected_indicators(indicator_id)
        predictions = []
        
        for effect in affected:
            # Calculate expected impact
            expected_change = change_magnitude * effect['strength']
            
            # Get current value of affected indicator
            affected_indicator = get_indicator_value(effect['indicator_id'])
            predicted_value = affected_indicator + expected_change
            
            predictions.append({
                'indicator_id': effect['indicator_id'],
                'indicator_name': get_indicator_name(effect['indicator_id']),
                'current_value': affected_indicator,
                'predicted_value': predicted_value,
                'expected_change': expected_change,
                'time_to_effect': effect['time_lag_hours'],
                'confidence': effect['strength']
            })
        
        return predictions
```

**Example Usage:**

```python
# Fuel shortage index just spiked
fuel_shortage = get_indicator_value('fuel_shortage_index')
previous_value = get_historical_value('fuel_shortage_index', hours_ago=24)

change = fuel_shortage - previous_value

# Predict secondary effects
dependency_engine = IndicatorDependencyEngine()
predictions = dependency_engine.predict_secondary_effects(
    'fuel_shortage_index',
    fuel_shortage,
    change
)

# Output:
# [
#     {
#         'indicator_id': 'transport_disruption',
#         'predicted_value': 78,
#         'expected_change': +25,
#         'time_to_effect': 48 hours,
#         'confidence': 0.85
#     },
#     {
#         'indicator_id': 'consumer_confidence',
#         'predicted_value': 42,
#         'expected_change': -15,
#         'time_to_effect': 72 hours,
#         'confidence': 0.65
#     }
# ]
```

---

## TREND ANALYSIS & FORECASTING {#trend-analysis}

### 2.10 TEMPORAL PATTERNS IN INDICATORS

#### Moving Averages

**Purpose**: Smooth out short-term fluctuations

```python
def calculate_moving_averages(indicator_id, periods=[7, 30, 90]):
    """
    Calculate multiple moving averages
    """
    
    moving_averages = {}
    
    for period in periods:
        # Query historical values
        historical_values = query_timescale(
            f"""
            SELECT time, value
            FROM indicator_values
            WHERE indicator_id = {indicator_id}
              AND time >= NOW() - INTERVAL '{period} days'
            ORDER BY time ASC
            """
        )
        
        if len(historical_values) >= period:
            values = [row['value'] for row in historical_values]
            ma = sum(values[-period:]) / period
            moving_averages[f'ma_{period}day'] = ma
    
    return moving_averages
```

#### Trend Detection

**Purpose**: Identify if indicator is rising, falling, or stable

```python
def detect_trend(indicator_id, window_days=30):
    """
    Determine trend direction and strength
    """
    
    # Get historical values
    values = get_historical_values(indicator_id, days=window_days)
    
    if len(values) < 5:
        return {'direction': 'unknown', 'strength': 0}
    
    # Calculate linear regression
    from scipy import stats
    
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
    
    # Strength based on R-squared
    strength = r_value ** 2  # 0 to 1
    
    # Calculate rate of change
    rate_of_change = (values[-1]['value'] - values[0]['value']) / window_days
    
    return {
        'direction': direction,
        'strength': strength,
        'slope': slope,
        'rate_of_change': rate_of_change,
        'r_squared': r_value ** 2,
        'confidence': 'high' if strength > 0.7 else 'medium' if strength > 0.4 else 'low'
    }
```

#### Forecasting

**Simple Forecasting: Linear Extrapolation**

```python
def forecast_linear(indicator_id, days_ahead=7):
    """
    Simple linear forecast based on recent trend
    """
    
    # Get last 30 days of data
    values = get_historical_values(indicator_id, days=30)
    
    if len(values) < 10:
        return None
    
    # Fit linear model
    x = np.arange(len(values))
    y = np.array([v['value'] for v in values])
    
    slope, intercept = np.polyfit(x, y, 1)
    
    # Project forward
    future_x = np.arange(len(values), len(values) + days_ahead)
    forecast_values = slope * future_x + intercept
    
    # Calculate confidence interval (simple approach)
    residuals = y - (slope * x + intercept)
    std_error = np.std(residuals)
    
    forecasts = []
    for i, future_value in enumerate(forecast_values):
        forecasts.append({
            'days_ahead': i + 1,
            'forecast_value': future_value,
            'lower_bound': future_value - 2 * std_error,
            'upper_bound': future_value + 2 * std_error
        })
    
    return forecasts
```

**Advanced Forecasting: ARIMA or Prophet (Iteration 2)**

```python
from prophet import Prophet

def forecast_prophet(indicator_id, days_ahead=7):
    """
    Use Facebook Prophet for time-series forecasting
    """
    
    # Get historical data
    values = get_historical_values(indicator_id, days=90)
    
    # Prepare data for Prophet
    df = pd.DataFrame({
        'ds': [v['timestamp'] for v in values],
        'y': [v['value'] for v in values]
    })
    
    # Fit model
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False  # Not enough data
    )
    model.fit(df)
    
    # Make forecast
    future = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future)
    
    # Extract forecasts
    forecasts = []
    for i in range(len(values), len(forecast)):
        forecasts.append({
            'date': forecast['ds'].iloc[i],
            'forecast_value': forecast['yhat'].iloc[i],
            'lower_bound': forecast['yhat_lower'].iloc[i],
            'upper_bound': forecast['yhat_upper'].iloc[i]
        })
    
    return forecasts
```

---

## ANOMALY DETECTION {#anomaly-detection}

### 2.11 IDENTIFYING UNUSUAL PATTERNS

**Purpose**: Alert when indicators deviate significantly from expected

#### Statistical Anomaly Detection

```python
def detect_anomalies(indicator_id, current_value):
    """
    Detect if current value is anomalous
    """
    
    # Get historical distribution
    historical = get_historical_values(indicator_id, days=90)
    historical_values = [v['value'] for v in historical]
    
    # Calculate statistics
    mean = np.mean(historical_values)
    std = np.std(historical_values)
    
    # Z-score
    z_score = (current_value - mean) / std if std > 0 else 0
    
    # Anomaly threshold: |z| > 2 (95% confidence)
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
        'deviation': current_value - mean,
        'historical_std': std
    }
```

#### Spike Detection

```python
def detect_spike(indicator_id, lookback_hours=24):
    """
    Detect rapid changes in indicator
    """
    
    # Get recent values
    current_value = get_current_value(indicator_id)
    value_24h_ago = get_historical_value(indicator_id, hours_ago=24)
    
    # Calculate change
    absolute_change = current_value - value_24h_ago
    percentage_change = (absolute_change / value_24h_ago * 100) if value_24h_ago != 0 else 0
    
    # Thresholds
    is_spike = abs(percentage_change) > 50  # 50% change in 24 hours
    
    if abs(percentage_change) > 100:
        spike_severity = 'extreme'
    elif abs(percentage_change) > 75:
        spike_severity = 'high'
    elif abs(percentage_change) > 50:
        spike_severity = 'moderate'
    else:
        spike_severity = 'none'
    
    direction = 'upward' if absolute_change > 0 else 'downward'
    
    return {
        'is_spike': is_spike,
        'severity': spike_severity,
        'direction': direction,
        'absolute_change': absolute_change,
        'percentage_change': percentage_change,
        'current_value': current_value,
        'previous_value': value_24h_ago
    }
```

---

## NARRATIVE GENERATION {#narrative-generation}

### 2.12 AUTO-GENERATING EXPLANATIONS

**Purpose**: Translate numbers into human-readable insights

```python
class IndicatorNarrativeGenerator:
    
    def generate_narrative(self, indicator_id, current_value, context):
        """
        Generate human-readable explanation of indicator state
        """
        
        indicator_def = get_indicator_definition(indicator_id)
        
        # Get supporting data
        trend = detect_trend(indicator_id)
        anomaly = detect_anomalies(indicator_id, current_value)
        contributing_articles = get_contributing_articles(indicator_id)
        
        # Build narrative components
        headline = self._generate_headline(indicator_def, current_value, trend, anomaly)
        summary = self._generate_summary(indicator_def, current_value, trend, contributing_articles)
        key_factors = self._extract_key_factors(contributing_articles)
        comparison = self._generate_comparison(indicator_def, current_value, context)
        implications = self._generate_implications(indicator_def, current_value, trend)
        
        return {
            'headline': headline,
            'summary': summary,
            'key_factors': key_factors,
            'comparison': comparison,
            'implications': implications
        }
    
    def _generate_headline(self, indicator_def, value, trend, anomaly):
        """Generate attention-grabbing headline"""
        
        name = indicator_def['display_name']
        
        if anomaly['is_anomaly'] and anomaly['severity'] == 'extreme':
            return f"⚠️ {name} Reaches Extreme Level"
        
        elif trend['direction'] == 'rising' and trend['strength'] > 0.7:
            return f"📈 {name} Shows Strong Upward Trend"
        
        elif trend['direction'] == 'falling' and trend['strength'] > 0.7:
            return f"📉 {name} Declining Significantly"
        
        else:
            # Classify based on value
            thresholds = get_indicator_thresholds(indicator_def['indicator_id'])
            level = self._classify_value(value, thresholds)
            return f"{name}: {level}"
    
    def _generate_summary(self, indicator_def, value, trend, articles):
        """Generate 2-3 sentence summary"""
        
        name = indicator_def['display_name']
        
        # Sentence 1: Current state
        summary = f"The {name} is currently at {value:.1f}. "
        
        # Sentence 2: Trend
        if trend['direction'] == 'rising':
            summary += f"This represents a {abs(trend['rate_of_change']):.1f} point increase over the past month. "
        elif trend['direction'] == 'falling':
            summary += f"This is down {abs(trend['rate_of_change']):.1f} points from last month. "
        else:
            summary += "The indicator has remained relatively stable recently. "
        
        # Sentence 3: Data basis
        summary += f"This assessment is based on {len(articles)} news articles from credible sources."
        
        return summary
    
    def _extract_key_factors(self, articles):
        """Extract main contributing factors"""
        
        # Group articles by topic
        topics = {}
        for article in articles:
            for keyword in article['initial_classification']['keywords'][:3]:  # Top 3 keywords
                if keyword not in topics:
                    topics[keyword] = []
                topics[keyword].append(article)
        
        # Sort by frequency
        sorted_topics = sorted(topics.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Generate factor descriptions
        factors = []
        for topic, topic_articles in sorted_topics[:5]:  # Top 5 topics
            count = len(topic_articles)
            example = topic_articles[0]['content']['title']
            
            factors.append(f"{count} articles about {topic} (e.g., \"{example}\")")
        
        return factors
    
    def _generate_comparison(self, indicator_def, current_value, context):
        """Compare to historical context"""
        
        historical_avg = context.get('historical_average', current_value)
        deviation = ((current_value - historical_avg) / historical_avg * 100) if historical_avg != 0 else 0
        
        if abs(deviation) < 10:
            return f"This is close to the historical average of {historical_avg:.1f}."
        elif deviation > 0:
            return f"This is {abs(deviation):.0f}% above the historical average of {historical_avg:.1f}."
        else:
            return f"This is {abs(deviation):.0f}% below the historical average of {historical_avg:.1f}."
    
    def _generate_implications(self, indicator_def, value, trend):
        """Generate business implications"""
        
        # Load implication templates from database
        implications_db = get_indicator_implications(indicator_def['indicator_id'])
        
        # Select appropriate implications based on current state
        thresholds = get_indicator_thresholds(indicator_def['indicator_id'])
        level = self._classify_value(value, thresholds)
        
        # Find matching implications
        relevant_implications = [
            imp for imp in implications_db 
            if imp['level'] == level
        ]
        
        return [imp['text'] for imp in relevant_implications[:3]]  # Top 3
```

---

## ITERATION 1 IMPLEMENTATION CHECKLIST {#iteration-1-checklist}

### Week 1-2 Deliverables - FOUNDATION

#### Day 1-2: Database & Configuration Setup

```
□ Set up database schemas:
  □ PostgreSQL: indicator_definitions, dependencies, keywords, thresholds
  □ TimescaleDB: indicator_values, indicator_events, indicator_trends
  □ MongoDB: indicator_calculations, indicator_narratives
  □ Redis: caching structure

□ Create indicator taxonomy:
  □ Define 20-30 core indicators across PESTEL categories
  □ Populate indicator_definitions table
  □ Configure calculation types for each
  
□ Mock data preparation:
  □ Create 100-200 mock articles
  □ Cover diverse scenarios (protests, economic news, disasters)
  □ Include varied timestamps (last 30 days)

□ Test database connections and queries
```

#### Day 3-4: Rule-Based Classification

```
□ Implement keyword mapping system:
  □ Define keywords for each indicator
  □ Store in indicator_keywords table
  □ Include weights and context rules

□ Build rule-based classifier:
  □ Keyword matching engine
  □ Context validation logic
  □ Confidence scoring
  □ Output: article-indicator mappings

□ Test with mock data:
  □ Verify correct indicator assignments
  □ Check confidence scores
  □ Validate edge cases

□ Performance: Process 100 articles in <5 seconds
```

#### Day 5-7: Basic Indicator Calculations

```
□ Implement calculation engines:
  □ Frequency-based calculator
  □ Sentiment-based calculator
  □ Numeric extraction calculator
  
□ Build weighting system:
  □ Recency weight calculator
  □ Credibility weight calculator
  □ Volume weight calculator
  □ Combined weighting function

□ Calculate 10 core indicators:
  □ Political Unrest Index
  □ Consumer Confidence Proxy
  □ Inflation Pressure Index
  □ Economic Health Index (composite)
  □ Social Sentiment Score
  □ (5 more of your choice)

□ Store results in TimescaleDB:
  □ Indicator values with timestamps
  □ Calculation metadata
  □ Confidence scores

□ Test end-to-end:
  □ Mock articles → Classification → Calculation → Storage
  □ Verify data in all databases
```

#### Day 8-9: Trend Analysis

```
□ Implement moving averages:
  □ 7-day, 30-day moving averages
  □ Store in indicator_trends table

□ Build trend detector:
  □ Direction (rising/falling/stable)
  □ Strength calculation
  □ Rate of change

□ Test with time-series data:
  □ Generate historical data for indicators
  □ Verify trend detection accuracy
```

#### Day 10-11: Basic Anomaly Detection

```
□ Implement statistical anomaly detection:
  □ Z-score calculation
  □ Threshold-based alerts
  □ Severity classification

□ Build spike detector:
  □ Rapid change detection
  □ Percentage change thresholds

□ Create event logging:
  □ Log anomalies to indicator_events table
  □ Include context and severity
```

#### Day 12-14: Integration & Testing

```
□ Build indicator dashboard (simple):
  □ Display current values for all indicators
  □ Show trends (up/down/stable arrows)
  □ Highlight anomalies in red

□ Create data export functions:
  □ Query interface for Layer 3
  □ JSON/CSV export formats

□ End-to-end integration test:
  □ Feed 200 mock articles
  □ Generate all indicators
  □ Verify calculations
  □ Check database consistency

□ Performance optimization:
  □ Batch processing
  □ Query optimization
  □ Index tuning

□ Documentation:
  □ Indicator calculation guide
  □ API documentation
  □ Database schema docs
```

---

## ITERATION 2: ADVANCED FEATURES {#iteration-2-features}

### Days 15-21: ML & Advanced Capabilities

#### 2.1 ML Classification System

```
□ Prepare training data:
  □ Manually label 500-1,000 articles
  □ Create balanced dataset across indicators
  □ Split train/validation/test sets

□ Train ML classifier:
  □ Choose approach (XGBoost or BERT)
  □ Feature engineering (if XGBoost)
  □ Model training and validation
  □ Hyperparameter tuning

□ Deploy classifier:
  □ Integration with existing pipeline
  □ Hybrid mode (rule-based + ML)
  □ Performance monitoring

□ Evaluate accuracy:
  □ F1 score > 0.75 target
  □ Precision/recall analysis
  □ Confusion matrix review
```

#### 2.2 Entity Extraction Enhancement

```
□ Implement advanced entity extraction:
  □ spaCy integration
  □ Custom entity recognizers
  □ Numeric value extraction
  □ Date parsing

□ Entity-based indicator features:
  □ Geographic concentration analysis
  □ Organization network mapping
  □ Amount aggregation (prices, revenues)

□ Store entities in MongoDB:
  □ Link to articles and indicators
  □ Enable entity-based queries
```

#### 2.3 Composite Indicators

```
□ Build composite indicator engine:
  □ Define 5-10 composite indicators
  □ Implement weighted aggregation
  □ Dependency tracking

□ Create dependency mapper:
  □ Causal relationship modeling
  □ Time-lag analysis
  □ Secondary effect prediction

□ Visualize dependencies:
  □ Graph representation
  □ Impact flow diagrams
```

#### 2.4 Advanced Forecasting

```
□ Implement Prophet forecasting:
  □ Train on historical data
  □ 7-day forecasts for key indicators
  □ Confidence intervals

□ Forecast evaluation:
  □ Backtesting on historical data
  □ Accuracy metrics (MAPE, RMSE)
  □ Model refinement

□ Automated forecast generation:
  □ Daily forecast updates
  □ Forecast vs. actual tracking
```

#### 2.5 Narrative Generation

```
□ Build narrative generator:
  □ Template-based system
  □ Context-aware generation
  □ Multi-level detail (headline, summary, full)

□ Create narrative library:
  □ Templates for each indicator
  □ Dynamic content insertion
  □ Sentiment-aware language

□ Store narratives:
  □ MongoDB indicator_narratives
  □ Version tracking
  □ Language support (start with English)
```

---

## INTEGRATION WITH LAYER 3 {#integration-layer3}

### 2.13 DATA HANDOFF TO OPERATIONAL INDICATORS

**What Layer 2 Provides to Layer 3:**

```json
{
    "timestamp": "2025-11-30T10:00:00Z",
    "indicators": [
        {
            "indicator_id": 1,
            "indicator_code": "POL_UNREST_01",
            "indicator_name": "Political Unrest Index",
            "pestel_category": "Political",
            "subcategory": "Civil Unrest",
            
            "current_value": 78.5,
            "normalized_value": 0.785,
            
            "trend": {
                "direction": "rising",
                "strength": 0.82,
                "rate_of_change": 2.3,
                "ma_7day": 65.2,
                "ma_30day": 52.1
            },
            
            "anomaly": {
                "is_anomaly": true,
                "severity": "significant",
                "z_score": 2.4,
                "expected_value": 52.0,
                "deviation": 26.5
            },
            
            "quality": {
                "confidence": 0.85,
                "contributing_articles": 15,
                "data_points": 15,
                "quality_flags": []
            },
            
            "geographic_distribution": {
                "Colombo": 12,
                "Kandy": 2,
                "Galle": 1
            },
            
            "narrative": {
                "headline": "⚠️ Political Unrest Index Elevated",
                "summary": "The Political Unrest Index increased 35% today to 78.5...",
                "implications": [
                    "Transportation disruptions likely",
                    "Business operations may face delays"
                ]
            }
        },
        // ... more indicators
    ],
    
    "composite_indicators": {
        "economic_health_index": 62.4,
        "national_stability_score": 55.8
    },
    
    "alerts": [
        {
            "indicator_id": 1,
            "alert_type": "threshold_breach",
            "severity": "high",
            "message": "Political Unrest Index exceeded high threshold"
        }
    ]
}
```

**Query Interface:**

```python
# Layer 3 can query Layer 2 data

class Layer2DataProvider:
    
    def get_current_indicators(self, pestel_category=None):
        """Get latest values for all indicators"""
        pass
    
    def get_indicator_history(self, indicator_id, days=30):
        """Get time-series data for specific indicator"""
        pass
    
    def get_trending_indicators(self, direction='rising', min_strength=0.7):
        """Get indicators with strong trends"""
        pass
    
    def get_anomalous_indicators(self, min_severity='moderate'):
        """Get indicators with detected anomalies"""
        pass
    
    def get_geographic_hotspots(self, pestel_category=None):
        """Get regions with high indicator activity"""
        pass
```

---

## TESTING STRATEGY {#testing-strategy}

### 2.14 VALIDATION & QUALITY ASSURANCE

#### Unit Tests

```
Test Coverage Target: 80%+

Test Categories:
├── Indicator calculation functions
│   ├── Frequency-based calculations
│   ├── Sentiment aggregations
│   ├── Weighted scoring
│   └── Composite indicator logic
│
├── Classification systems
│   ├── Keyword matching
│   ├── ML predictions (mock model)
│   └── Hybrid combination
│
├── Trend analysis
│   ├── Moving averages
│   ├── Trend detection
│   └── Forecasting (basic)
│
└── Anomaly detection
    ├── Statistical methods
    └── Spike detection
```

#### Integration Tests

```
End-to-End Flows:
├── Mock articles → Classification → Calculation → Storage → Retrieval
├── Time-series data generation → Trend analysis → Forecasting
├── Anomaly generation → Detection → Alert creation
└── Composite indicator calculation from components

Test Scenarios:
├── Normal operations (steady state)
├── Crisis scenario (rapid indicator changes)
├── Data gaps (missing articles)
├── Conflicting signals (mixed sentiments)
└── Edge cases (extreme values, zero data)
```

#### Validation Tests

```
Indicator Quality Validation:
├── Manual review of 50 random indicator values
├── Expert validation (domain experts review results)
├── Historical backtesting (compare to known events)
└── Cross-validation with official statistics (where available)

Expected Accuracy:
├── Indicator assignments: 80%+ correct
├── Sentiment classification: 75%+ agreement with human labels
├── Trend direction: 85%+ accuracy
└── Anomaly detection: <10% false positive rate
```

---

## PERFORMANCE & OPTIMIZATION {#performance-optimization}

### 2.15 SCALING & EFFICIENCY

#### Performance Targets

```
Processing Speed:
├── Article classification: <500ms per article
├── Indicator calculation: <2 seconds for all indicators
├── Trend analysis: <1 second per indicator
└── Dashboard data query: <3 seconds

Throughput:
├── Handle 1,000 articles/hour
├── Calculate 50+ indicators every 15 minutes
├── Support 100+ concurrent dashboard users
```

#### Optimization Strategies

```
1. Caching:
   ├── Redis cache for current indicator values (TTL: 5 minutes)
   ├── Pre-computed moving averages (update hourly)
   └── Cached ML model predictions for similar articles

2. Batch Processing:
   ├── Process articles in batches of 50
   ├── Bulk database inserts
   └── Parallel indicator calculations

3. Database Optimization:
   ├── Proper indexing on all query columns
   ├── TimescaleDB continuous aggregates
   ├── PostgreSQL connection pooling
   └── Query result caching

4. Async Processing:
   ├── Queue-based architecture
   ├── Background workers for heavy calculations
   └── Non-blocking API endpoints
```

---

## FINAL ARCHITECTURE SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│                LAYER 2 COMPLETE SYSTEM                       │
└─────────────────────────────────────────────────────────────┘

INPUT (From Layer 1):           OUTPUT (To Layer 3):
├── Processed articles          ├── 50+ PESTEL indicators
├── Entities & keywords         ├── Trend analysis
├── Sentiment scores            ├── Anomaly alerts
└── Credibility metadata        ├── Geographic patterns
                                └── Narrative explanations

DATABASES:
├── PostgreSQL (Indicator definitions, relationships)
├── TimescaleDB (Time-series values, trends)
├── MongoDB (Calculation details, narratives)
└── Redis (Real-time cache)

PROCESSING PIPELINE:
Articles → Rule Classification → ML Classification → Entity Extraction →
Indicator Calculation → Weighting → Trend Analysis → Anomaly Detection →
Composite Indicators → Narrative Generation → Storage → Layer 3

KEY FEATURES:
✓ Hybrid classification (rule-based + ML)
✓ Multi-factor weighting system
✓ Real-time trend detection
✓ Statistical anomaly detection
✓ Composite indicator support
✓ Dependency mapping
✓ Auto-generated narratives
✓ Geographic analysis
✓ Forecasting capabilities
```

---

**End of Part 2**

This completes the comprehensive architectural blueprint for Layer 2. You now have:
- Complete indicator taxonomy (50+ indicators)
- Database schemas for all storage needs
- Classification pipeline (rule-based + ML)
- Calculation methodologies for all indicator types
- Trend analysis and forecasting
- Anomaly detection
- Narrative generation
- Integration interfaces
- Implementation checklist
- Testing and optimization strategies

Ready for Claude Code to implement systematically!
