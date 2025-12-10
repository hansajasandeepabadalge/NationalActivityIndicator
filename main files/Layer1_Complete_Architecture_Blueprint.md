# LAYER 1: DATA ACQUISITION & PREPROCESSING ENGINE
## Comprehensive Architectural Blueprint & Implementation Plan

---

## TABLE OF CONTENTS

1. [Phase 0: Strategic Analysis & Design Decisions](#phase-0)
2. [Architectural Overview](#architectural-overview)
3. [Iteration 1: Minimum Viable Foundation](#iteration-1)
4. [Database Schemas](#database-schemas)
5. [Source Configuration Framework](#source-configuration)
6. [Scraper Engine Architecture](#scraper-engine)
7. [Job Scheduling & Orchestration](#job-scheduling)
8. [Data Validation Pipeline](#data-validation)
9. [Data Cleaning Pipeline](#data-cleaning)
10. [Language Detection & Translation](#language-translation)
11. [Deduplication Engine](#deduplication)
12. [Quality Assessment & Credibility Scoring](#quality-assessment)
13. [Data Persistence & Storage Patterns](#data-persistence)
14. [Iteration 1 Implementation Checklist](#iteration-1-checklist)
15. [Iteration 2: Advanced Features](#iteration-2)
16. [Critical Technical Specifications](#technical-specs)
17. [Integration Points with Layer 2](#integration-layer2)
18. [Deployment Architecture](#deployment)
19. [Testing Strategy](#testing)
20. [Success Metrics](#success-metrics)

---

## PHASE 0: STRATEGIC ANALYSIS & DESIGN DECISIONS {#phase-0}

### System Design Philosophy

**Core Principles:**
1. **Modularity**: Each component operates independently, communicates via well-defined interfaces
2. **Scalability**: Start simple, architecture supports complexity later
3. **Resilience**: Failures in one component don't crash the system
4. **Observability**: Every operation logged, monitored, measurable
5. **Configuration-Driven**: Business logic in config files, not hardcoded

**Key Architectural Decision: Multi-Database Strategy**

**Why Multiple Databases?**
- **Document DB (MongoDB)**: Unstructured content, flexible schemas, fast writes
- **Relational DB (PostgreSQL)**: Structured metadata, complex queries, relationships
- **Time-Series DB (TimescaleDB/InfluxDB)**: Temporal analysis, trend detection
- **Cache Layer (Redis)**: Fast lookups, job queues, temporary storage

**Database Responsibility Matrix:**
```
MongoDB:          Raw content, full articles, social media posts
PostgreSQL:       Sources registry, categories, entity relationships, configurations
TimescaleDB:      Metrics over time, mention frequencies, sentiment trends
Redis:            Scraping queue, processed IDs cache, rate limiting counters
```

---

## ARCHITECTURAL OVERVIEW {#architectural-overview}

### The Complete Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: DATA ACQUISITION                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   SOURCES    │───▶│  SCHEDULERS  │───▶│   SCRAPERS   │
│  (Configs)   │    │  (Triggers)  │    │  (Workers)   │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
                    ┌────────────────────────────────────┐
                    │      RAW DATA STORAGE              │
                    │  MongoDB: raw_articles collection  │
                    └────────────────────────────────────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  LANGUAGE    │◀───│  CLEANING    │◀───│ VALIDATION   │
│  DETECTION   │    │  PIPELINE    │    │   CHECKS     │
└──────────────┘    └──────────────┘    └──────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │   TRANSLATION ENGINE    │
              │   (Multi-language)      │
              └─────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  DEDUPLICATION ENGINE   │
              │  (Similarity Detection) │
              └─────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │   QUALITY ASSESSMENT    │
              │   (Credibility Scoring) │
              └─────────────────────────┘
                           │
                           ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  MongoDB:    │    │ PostgreSQL:  │    │ TimescaleDB: │
    │  processed_  │    │  metadata    │    │  metrics     │
    │  articles    │    │  tables      │    │  timeseries  │
    └──────────────┘    └──────────────┘    └──────────────┘
```

---

## ITERATION 1: MINIMUM VIABLE FOUNDATION (Days 1-2) {#iteration-1}

### Goal: Get data flowing from 3 sources into database

### Overview
This iteration focuses on building the core foundation that can successfully scrape, validate, and store articles from at least 3 news sources. The emphasis is on simplicity and reliability rather than advanced features.

**What We're Building:**
- Basic scraper framework (RSS-based)
- Core database schemas
- Simple validation
- Basic cleaning
- Language detection and translation
- URL-based duplicate detection

**What We're NOT Building Yet:**
- Advanced scrapers (JavaScript-heavy sites)
- Social media integration
- Semantic deduplication
- Bias detection
- Advanced quality scoring

---

## DATABASE SCHEMAS {#database-schemas}

### 1.1 DATABASE SCHEMA INITIALIZATION

#### PostgreSQL Schema (Metadata & Configuration)

**Table 1: `sources`**
```sql
/*
Purpose: Registry of all data sources
Responsibility: Single source of truth for what we scrape
*/

CREATE TABLE sources (
    source_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(20) NOT NULL,  -- 'news', 'social', 'government', 'api'
    base_url VARCHAR(500) NOT NULL,
    language VARCHAR(10) NOT NULL,     -- 'en', 'si', 'ta', 'multi'
    
    -- Operational metadata
    credibility_score DECIMAL(3,2) DEFAULT 0.75,  -- 0.00 to 1.00
    update_frequency_minutes INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Scraping configuration (JSON blob for flexibility)
    scrape_config JSONB NOT NULL,
    
    -- Tracking
    last_scraped_at TIMESTAMP,
    last_successful_scrape TIMESTAMP,
    consecutive_failures INTEGER DEFAULT 0,
    total_articles_collected INTEGER DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for quick active source lookups
CREATE INDEX idx_sources_active ON sources(is_active);
CREATE INDEX idx_sources_next_scrape ON sources(last_scraped_at) 
    WHERE is_active = TRUE;
```

**Table 2: `categories`**
```sql
/*
Purpose: Hierarchical category taxonomy
Responsibility: Standardized classification system
*/

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    parent_category_id INTEGER REFERENCES categories(category_id),
    level INTEGER NOT NULL,  -- 1=primary, 2=secondary, 3=tertiary
    description TEXT,
    keywords TEXT[],  -- Array of relevant keywords
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sample data structure:
-- Level 1: ECONOMIC (id=1, parent=NULL)
-- Level 2: Financial Markets (id=10, parent=1)
-- Level 3: Stock Market (id=101, parent=10)

CREATE INDEX idx_categories_parent ON categories(parent_category_id);
CREATE INDEX idx_categories_level ON categories(level);
```

**Table 3: `scrape_jobs`**
```sql
/*
Purpose: Job queue and execution tracking
Responsibility: Orchestrate scraping operations
*/

CREATE TABLE scrape_jobs (
    job_id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(source_id),
    
    -- Job metadata
    job_type VARCHAR(20),  -- 'full', 'incremental', 'realtime'
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    priority INTEGER DEFAULT 5,  -- 1=highest, 10=lowest
    
    -- Execution tracking
    scheduled_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Results
    articles_found INTEGER DEFAULT 0,
    articles_new INTEGER DEFAULT 0,
    articles_updated INTEGER DEFAULT 0,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scrape_jobs_pending ON scrape_jobs(status, priority, scheduled_at)
    WHERE status = 'pending';
CREATE INDEX idx_scrape_jobs_source ON scrape_jobs(source_id, created_at DESC);
```

**Table 4: `article_metadata`**
```sql
/*
Purpose: Relational metadata about articles
Responsibility: Queryable structured data
*/

CREATE TABLE article_metadata (
    metadata_id SERIAL PRIMARY KEY,
    article_id VARCHAR(50) NOT NULL UNIQUE,  -- Links to MongoDB document
    source_id INTEGER REFERENCES sources(source_id),
    
    -- Core identifiers
    url VARCHAR(1000) NOT NULL UNIQUE,
    url_hash CHAR(64) NOT NULL,  -- SHA256 for quick duplicate detection
    
    -- Timestamps
    published_at TIMESTAMP,
    scraped_at TIMESTAMP NOT NULL,
    processed_at TIMESTAMP,
    
    -- Classification
    language_detected VARCHAR(10),
    content_type VARCHAR(20),  -- 'article', 'brief', 'announcement', 'report'
    
    -- Processing status
    processing_stage VARCHAR(30) DEFAULT 'raw',
    -- Stages: raw → validated → cleaned → translated → deduplicated → categorized
    
    -- Quality metrics
    credibility_score DECIMAL(3,2),
    word_count INTEGER,
    has_translation BOOLEAN DEFAULT FALSE,
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of VARCHAR(50),  -- article_id of original
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_article_url_hash ON article_metadata(url_hash);
CREATE INDEX idx_article_published ON article_metadata(published_at DESC);
CREATE INDEX idx_article_stage ON article_metadata(processing_stage);
CREATE INDEX idx_article_source_date ON article_metadata(source_id, published_at DESC);
```

**Table 5: `source_category_mappings`**
```sql
/*
Purpose: Map source's categories to our standardized taxonomy
Responsibility: Handle pre-categorized sources
*/

CREATE TABLE source_category_mappings (
    mapping_id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(source_id),
    source_category_label VARCHAR(100) NOT NULL,  -- What THEY call it
    our_category_id INTEGER REFERENCES categories(category_id),  -- What WE call it
    confidence DECIMAL(3,2) DEFAULT 1.00,
    
    UNIQUE(source_id, source_category_label)
);

-- Example: Daily Mirror calls it "Business" → We map to category_id=1 (ECONOMIC)
```

#### MongoDB Schema (Content Storage)

**Collection 1: `raw_articles`**
```javascript
/*
Purpose: Unprocessed scraped content as-is
Retention: Keep for audit trail, debugging
*/

{
    _id: ObjectId("..."),
    article_id: "ada_derana_2025_001234",  // Unique identifier
    source: {
        source_id: 1,
        name: "Ada Derana",
        url: "https://adaderana.lk/news/123456"
    },
    
    scrape_metadata: {
        job_id: 5678,
        scraped_at: ISODate("2025-11-29T10:30:00Z"),
        scraper_version: "1.0.0"
    },
    
    raw_content: {
        html: "<html>...</html>",  // Full HTML if needed
        title: "Government announces fuel price change",
        body: "Full article text in original language...",
        author: "Staff Reporter",
        publish_date: "2025-11-28T15:00:00Z",
        images: [
            {url: "https://...", caption: "..."}
        ],
        metadata: {
            source_category: "Economy",  // Their classification
            tags: ["fuel", "prices", "economy"]
        }
    },
    
    validation: {
        is_valid: true,
        validation_errors: [],
        word_count: 456
    }
}

// Indexes
db.raw_articles.createIndex({"article_id": 1}, {unique: true})
db.raw_articles.createIndex({"scrape_metadata.scraped_at": -1})
db.raw_articles.createIndex({"source.source_id": 1, "raw_content.publish_date": -1})
```

**Collection 2: `processed_articles`**
```javascript
/*
Purpose: Cleaned, translated, enriched content
Primary Use: Feed to Layer 2 for analysis
*/

{
    _id: ObjectId("..."),
    article_id: "ada_derana_2025_001234",  // Same ID as raw
    
    content: {
        title_original: "රජය ඉන්ධන මිල වෙනස් කිරීම නිවේදනය කරයි",
        title_english: "Government announces fuel price change",
        
        body_original: "Original Sinhala text...",
        body_english: "Translated English text...",
        
        summary: "3-sentence summary generated...",  // Optional for Iteration 1
        
        language_original: "si",
        translation_confidence: 0.92
    },
    
    extraction: {
        publish_timestamp: ISODate("2025-11-28T15:00:00Z"),
        author: "Staff Reporter",
        
        // Basic extraction for Iteration 1, enhanced in Iteration 2
        keywords_extracted: ["fuel", "prices", "government", "increase"],
        
        entities: {  // Placeholder for Iteration 2
            locations: [],
            organizations: [],
            persons: [],
            amounts: []
        }
    },
    
    processing_pipeline: {
        stages_completed: ["validation", "cleaning", "language_detection", "translation"],
        last_updated: ISODate("2025-11-29T10:35:00Z"),
        processing_version: "1.0.0"
    },
    
    quality: {
        credibility_score: 0.85,
        bias_indicator: "neutral",  // Placeholder for Iteration 2
        is_clean: true,
        quality_flags: []
    },
    
    deduplication: {
        is_duplicate: false,
        duplicate_cluster_id: null,
        similarity_hash: "abc123def456...",  // For fast comparison
        similar_articles: []  // List of related article_ids
    }
}

// Indexes
db.processed_articles.createIndex({"article_id": 1}, {unique: true})
db.processed_articles.createIndex({"deduplication.similarity_hash": 1})
db.processed_articles.createIndex({"extraction.publish_timestamp": -1})
db.processed_articles.createIndex({"quality.credibility_score": -1})
db.processed_articles.createIndex({"processing_pipeline.stages_completed": 1})
```

**Collection 3: `social_media_trends`** (Iteration 2+)
```javascript
/*
Purpose: Aggregated social media signals
*/

{
    _id: ObjectId("..."),
    platform: "twitter",
    
    trend: {
        keyword: "#FuelCrisis",
        type: "hashtag",  // 'hashtag', 'keyword', 'topic'
        
        metrics: {
            mention_count: 5420,
            unique_users: 3200,
            retweets: 890,
            engagement_score: 7.8
        },
        
        sentiment: {
            positive: 120,
            neutral: 1200,
            negative: 3100,
            overall_score: -0.42
        },
        
        geographic_distribution: {
            "Colombo": 3200,
            "Kandy": 800,
            "Galle": 420
        },
        
        top_influencers: [
            {username_hash: "abc123", followers: 50000, mentions: 15}
        ]
    },
    
    time_window: {
        start: ISODate("2025-11-29T00:00:00Z"),
        end: ISODate("2025-11-29T12:00:00Z"),
        duration_hours: 12
    },
    
    velocity: {
        previous_12h_count: 1200,
        growth_rate: 4.52,  // 452% increase
        is_trending: true
    }
}

// Indexes
db.social_media_trends.createIndex({"trend.keyword": 1, "time_window.start": -1})
db.social_media_trends.createIndex({"velocity.is_trending": 1})
```

#### TimescaleDB Schema (Time-Series Metrics)

**Hypertable 1: `mention_timeseries`**
```sql
/*
Purpose: Track keyword/topic mentions over time
Use Case: Detect spikes, trends, anomalies
*/

CREATE TABLE mention_timeseries (
    time TIMESTAMPTZ NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    source_type VARCHAR(20) NOT NULL,  -- 'news', 'social', 'all'
    
    -- Metrics
    mention_count INTEGER NOT NULL,
    unique_sources INTEGER,
    
    -- Sentiment aggregate
    avg_sentiment DECIMAL(4,3),  -- -1.000 to 1.000
    sentiment_variance DECIMAL(4,3),
    
    -- Geography
    top_location VARCHAR(50),
    
    PRIMARY KEY (time, keyword, source_type)
);

-- Convert to hypertable (TimescaleDB specific)
SELECT create_hypertable('mention_timeseries', 'time');

-- Create index for fast keyword lookups
CREATE INDEX idx_mention_keyword ON mention_timeseries(keyword, time DESC);
```

**Hypertable 2: `source_health_metrics`**
```sql
/*
Purpose: Monitor scraper performance and source reliability
Use Case: Detect failing sources, optimize schedules
*/

CREATE TABLE source_health_metrics (
    time TIMESTAMPTZ NOT NULL,
    source_id INTEGER NOT NULL,
    
    -- Performance metrics
    scrape_duration_seconds INTEGER,
    articles_collected INTEGER,
    errors_count INTEGER,
    success_rate DECIMAL(4,3),
    
    -- Content quality
    avg_credibility DECIMAL(3,2),
    avg_word_count INTEGER,
    duplicate_rate DECIMAL(4,3),
    
    PRIMARY KEY (time, source_id)
);

SELECT create_hypertable('source_health_metrics', 'time');
```

#### Redis Schema (Cache & Queue)

**Key Patterns:**

```
/*
Purpose: Fast lookups, job queues, rate limiting
*/

Key Patterns:
├── scrape:queue:high_priority     (List: Job IDs for urgent scraping)
├── scrape:queue:normal            (List: Regular scraping jobs)
├── scrape:queue:low_priority      (List: Background scraping)
│
├── processed:article:{article_id} (Set: Track processed articles, TTL 24h)
├── url:seen:{url_hash}            (String: Quick duplicate URL check, TTL 48h)
│
├── ratelimit:{source_id}:{hour}   (Counter: Track requests per source)
├── translation:cache:{text_hash}  (String: Cached translations, TTL 30 days)
│
└── stats:realtime:{metric}        (Hash: Real-time dashboard metrics)
```

---

## SOURCE CONFIGURATION FRAMEWORK {#source-configuration}

### 1.2 SOURCE CONFIGURATION FRAMEWORK

#### The Configuration-Driven Architecture

**Design Philosophy:**
- **Zero-code source addition**: Adding a source = Adding a config file
- **Template-based**: Pre-defined patterns for common site structures
- **Fallback mechanisms**: Multiple extraction strategies per field

#### Configuration File Structure (YAML Format)

**File: `sources/ada_derana.yaml`**
```yaml
metadata:
  name: "Ada Derana"
  source_type: "news"
  base_url: "https://www.adaderana.lk"
  language: "multi"  # Supports both Sinhala and English
  credibility_score: 0.90
  update_frequency_minutes: 15

scraping:
  method: "html"  # Options: 'rss', 'html', 'api', 'selenium'
  
  entry_points:
    - url: "https://www.adaderana.lk/news.php"
      type: "article_list"
      pagination:
        enabled: true
        pattern: "https://www.adaderana.lk/news.php?page={page}"
        max_pages: 3
  
  selectors:
    article_list:
      container: "div.news-list"
      item: "div.news-item"
      link: "a.news-title::attr(href)"
      
    article_detail:
      title:
        - selector: "h1.news-title::text"
        - xpath: "//h1[@class='news-title']/text()"
        fallback: "meta[property='og:title']::attr(content)"
      
      body:
        - selector: "div.article-body"
        - xpath: "//div[@class='article-body']"
        cleanup:
          remove_tags: ["script", "style", "iframe", "ads"]
          remove_classes: [".advertisement", ".related-news"]
      
      publish_date:
        - selector: "span.publish-date::text"
        - xpath: "//time[@class='published']/@datetime"
        format: "%d %B %Y %H:%M"  # Example: "28 November 2025 15:30"
        fallback: "meta[property='article:published_time']::attr(content)"
      
      author:
        - selector: "span.author-name::text"
        - default: "Staff Reporter"
      
      category:
        - selector: "nav.breadcrumb li:nth-child(2) a::text"
        mapping_required: true
      
      images:
        - selector: "div.article-body img::attr(src)"
        caption: "img::attr(alt)"

  headers:
    User-Agent: "Mozilla/5.0 (Compatible; BusinessIntelBot/1.0)"
    Accept-Language: "en,si;q=0.9"

  rate_limiting:
    requests_per_minute: 30
    delay_between_requests: 2  # seconds
    respect_robots_txt: true

  validation:
    min_word_count: 50
    required_fields: ["title", "body", "publish_date"]
    url_pattern: "^https://www\\.adaderana\\.lk/news/"

preprocessing:
  language_detection:
    enabled: true
    fallback_language: "en"
  
  initial_cleaning:
    remove_urls: true
    remove_emails: true
    normalize_whitespace: true
    remove_html_entities: true

categorization:
  has_source_categories: true
  category_mappings:
    "Local News": "SOCIAL"
    "Breaking News": "GENERAL"
    "Business News": "ECONOMIC"
    "Political News": "POLITICAL"
    "Sports": "SPORTS"  # Will be filtered out later

error_handling:
  max_retries: 3
  retry_delay: 60  # seconds
  timeout: 30  # seconds per request
  on_failure:
    notify: true
    fallback_to_rss: false
```

**File: `sources/daily_mirror_rss.yaml`**
```yaml
metadata:
  name: "Daily Mirror"
  source_type: "news"
  base_url: "https://www.dailymirror.lk"
  language: "en"
  credibility_score: 0.85
  update_frequency_minutes: 30

scraping:
  method: "rss"
  
  entry_points:
    - url: "https://www.dailymirror.lk/rss"
      type: "rss_feed"
  
  rss_mappings:
    title: "title"
    link: "link"
    description: "description"
    publish_date: "pubDate"
    author: "dc:creator"
    category: "category"
  
  # For full article content, still need to fetch the page
  full_content_fetch:
    enabled: true
    selectors:
      body:
        - selector: "div.article-content"
      images:
        - selector: "div.article-content img::attr(src)"

categorization:
  has_source_categories: true
  category_mappings:
    "Business": "ECONOMIC"
    "Finance": "ECONOMIC.FINANCIAL_MARKETS"
    "Latest News": "GENERAL"
    "Politics": "POLITICAL"

rate_limiting:
  requests_per_minute: 20
  delay_between_requests: 3

validation:
  min_word_count: 50
  required_fields: ["title", "link"]

error_handling:
  max_retries: 3
  retry_delay: 60
  timeout: 30
```

**File: `sources/twitter_trends.yaml`**
```yaml
metadata:
  name: "Twitter Trending Topics (Sri Lanka)"
  source_type: "social"
  base_url: "https://api.twitter.com"
  language: "multi"
  credibility_score: 0.60  # Lower due to noise
  update_frequency_minutes: 60

scraping:
  method: "api"
  
  api:
    endpoint: "https://api.twitter.com/2/trends/place"
    authentication:
      type: "bearer_token"
      token_env_var: "TWITTER_BEARER_TOKEN"
    
    parameters:
      id: "23424778"  # WOEID for Sri Lanka
    
    rate_limits:
      requests_per_15min: 75

  data_extraction:
    trends:
      - field: "trends[].name"
      - field: "trends[].tweet_volume"
      - field: "trends[].url"

preprocessing:
  aggregation:
    method: "trend_analysis"
    min_tweet_volume: 100
    filter_hashtags_only: false

error_handling:
  max_retries: 2
  retry_delay: 300  # 5 minutes for API
  timeout: 15
```

#### Configuration Loader Module

**Responsibilities:**
1. **Load & Validate Configs**: Read YAML files, validate structure
2. **Dynamic Discovery**: Scan `sources/` directory for new configs
3. **Hot Reload**: Update configurations without restart
4. **Template Support**: Inherit from base templates

**Pseudo-Architecture:**
```
ConfigurationManager
├── load_all_sources()
│   └── For each YAML in sources/
│       ├── Validate schema
│       ├── Parse selectors
│       ├── Create Source object
│       └── Insert/update in PostgreSQL sources table
│
├── get_source_config(source_id) → SourceConfig
├── validate_config(yaml_content) → ValidationResult
└── reload_source(source_id) → Updated config
```

---

## SCRAPER ENGINE ARCHITECTURE {#scraper-engine}

### 1.3 SCRAPER ENGINE ARCHITECTURE

#### Multi-Method Scraping Framework

**Design: Strategy Pattern for Different Scraping Methods**

```
AbstractScraper (Base Class)
├── Methods: execute(), parse(), validate()
├── Subclasses:
    ├── RSSFeedScraper
    │   └── Fastest, most reliable when available
    │
    ├── HTMLStaticScraper
    │   └── BeautifulSoup/lxml for static sites
    │
    ├── JavaScriptScraper
    │   └── Selenium/Playwright for dynamic sites
    │
    └── APIScraper
        └── Direct API calls (social media, gov data)
```

#### Scraper Factory Pattern

**Pseudo-Logic:**
```python
class ScraperFactory:
    def create_scraper(source_config):
        if source_config.method == "rss":
            return RSSFeedScraper(source_config)
        elif source_config.method == "html":
            return HTMLStaticScraper(source_config)
        elif source_config.method == "selenium":
            return JavaScriptScraper(source_config)
        elif source_config.method == "api":
            return APIScraper(source_config)
        else:
            raise UnsupportedMethodError()
```

#### RSS Feed Scraper (Simplest, Start Here)

**Workflow:**
```
1. Fetch RSS feed XML from source_config.entry_points[0].url
2. Parse XML (using feedparser library)
3. For each entry:
   a. Extract: title, link, description, pubDate, category
   b. Generate article_id (hash of URL or use GUID)
   c. Check if URL already exists in Redis cache
   d. If new:
      - Optionally fetch full article content from link
      - Save to MongoDB raw_articles
      - Insert metadata to PostgreSQL
      - Add to processing queue
4. Update source.last_scraped_at
5. Log metrics
```

**Data Flow:**
```
RSS Feed URL
    ↓
feedparser.parse()
    ↓
For each item:
    ↓
{title, link, description, pubDate} → article_dict
    ↓
URL Hash Check (Redis: url:seen:{hash})
    ↓
If New → MongoDB.raw_articles.insert()
    ↓
PostgreSQL.article_metadata.insert()
    ↓
Redis.rpush("scrape:queue:normal", article_id)
```

#### HTML Static Scraper (For Non-RSS Sites)

**Workflow:**
```
1. Fetch article list page (entry_point URL)
2. Extract article links using selectors
3. For each link:
   a. Fetch article page
   b. Apply selectors to extract fields
   c. Use fallback selectors if primary fails
   d. Validate extracted data
   e. Save to MongoDB + PostgreSQL
4. Handle pagination (if enabled)
5. Respect rate limits
```

**Selector Application Logic:**
```
For field "title":
    Try selector[0] (CSS)
        ↓ (if fails)
    Try selector[1] (XPath)
        ↓ (if fails)
    Try fallback (meta tag)
        ↓ (if fails)
    Use default value OR mark as invalid
```

**Rate Limiting Implementation:**
```
Before each request:
    ↓
Check Redis: ratelimit:{source_id}:{current_hour}
    ↓
If count < max_requests_per_hour:
    ↓
Proceed with request
Increment Redis counter
    ↓
Else:
    ↓
Wait until next hour OR slow down
```

#### Content Extraction Strategy

**Multi-Level Extraction:**
```
Level 1: Try CSS Selector
    ↓ (Success?) → Return content
    ↓ (Fail)
Level 2: Try XPath
    ↓ (Success?) → Return content
    ↓ (Fail)
Level 3: Try Fallback (meta tags, JSON-LD)
    ↓ (Success?) → Return content
    ↓ (Fail)
Level 4: Default value OR Mark field as missing
```

---

## JOB SCHEDULING & ORCHESTRATION {#job-scheduling}

### 1.4 JOB SCHEDULING & ORCHESTRATION

#### Scheduler Architecture

**Components:**
```
JobScheduler
├── Cron-style timing (every 15 min, hourly, daily)
├── Priority queue management
├── Source-specific schedules
└── Adaptive scheduling (based on source activity)

JobExecutor
├── Worker pool (5-10 concurrent workers)
├── Job assignment logic
├── Failure handling & retries
└── Resource management
```

#### Scheduling Logic

**Priority-Based Scheduling:**
```
Priority Levels:
1. CRITICAL (1-2): Breaking news sources, real-time APIs
2. HIGH (3-4): Major news sites, active hours
3. MEDIUM (5-6): Standard sources, normal frequency
4. LOW (7-8): Background sources, archives
5. MINIMAL (9-10): Infrequent updates, secondary sources

Frequency Rules:
- CRITICAL: Every 15 minutes
- HIGH: Every 30 minutes (business hours), hourly (off-hours)
- MEDIUM: Every 1-2 hours
- LOW: Every 6-12 hours
- MINIMAL: Daily
```

**Adaptive Scheduling (Iteration 2):**
```
If source.articles_per_scrape > 10:
    Increase frequency (but respect rate limits)
    
If source.consecutive_failures > 3:
    Decrease frequency
    Notify admin

If source.articles_per_scrape == 0 for 24 hours:
    Check if source is down
    Reduce to minimal frequency
```

#### Job Queue Management

**Redis Queue Structure:**
```
scrape:queue:critical  → Processed first, every 5 seconds
scrape:queue:high      → Processed every 30 seconds
scrape:queue:normal    → Processed every 2 minutes
scrape:queue:low       → Processed every 10 minutes
```

**Job Creation Logic:**
```python
Every 15 minutes (cron job):
    For each active source:
        If time_since_last_scrape >= source.update_frequency:
            Create scrape_job in PostgreSQL
            Determine priority based on:
                - Source credibility
                - Update frequency
                - Recent article velocity
            Push job_id to appropriate Redis queue
            
Worker loop:
    While True:
        job_id = Redis.blpop(['scrape:queue:critical', 
                             'scrape:queue:high',
                             'scrape:queue:normal'], timeout=10)
        If job_id:
            Execute scraping job
            Update job status in PostgreSQL
            Record metrics
```

---

## DATA VALIDATION PIPELINE {#data-validation}

### 1.5 DATA VALIDATION PIPELINE

#### Validation Stages

**Stage 1: Structural Validation**
```
Check Required Fields:
├── title: Must exist, min length 10 chars
├── body: Must exist, min length 50 words
├── url: Must be valid URL format
├── publish_date: Must be parseable datetime
└── source_id: Must reference valid source

Data Type Validation:
├── Dates must be ISO format or parseable
├── URLs must match expected pattern
├── Word counts must be integers
└── Scores must be in valid ranges
```

**Stage 2: Content Quality Validation**
```
Quality Checks:
├── Word count >= configured minimum (default: 50)
├── Text is not gibberish (language detection succeeds)
├── Not pure HTML/code (detect <tags> without context)
├── Contains actual sentences (not just keywords)
└── Publish date is reasonable (not future, not >30 days old)

Spam Detection:
├── Excessive capitalization (>30% caps)
├── Repetitive content (same sentence 3+ times)
├── Keyword stuffing (same word >5% of total)
└── Known spam patterns (regex-based)
```

**Stage 3: Duplicate URL Check**
```
Fast Check (Redis):
    url_hash = SHA256(normalize_url(url))
    If Redis.exists(f"url:seen:{url_hash}"):
        Mark as duplicate
        Return existing article_id
    
Deep Check (PostgreSQL):
    If Redis check passes:
        Query: SELECT article_id FROM article_metadata 
               WHERE url_hash = {url_hash}
        If found:
            Mark as duplicate
            Update Redis cache
```

**Validation Result Structure:**
```
ValidationResult:
├── is_valid: Boolean
├── validation_errors: List[str]
│   ├── "missing_required_field: title"
│   ├── "content_too_short: 35 words < 50 minimum"
│   └── "invalid_date_format: publish_date"
├── quality_flags: List[str]
│   ├── "excessive_capitalization"
│   └── "possible_spam"
└── recommended_action: "accept" | "review" | "reject"
```

---

## DATA CLEANING PIPELINE {#data-cleaning}

### 1.6 DATA CLEANING PIPELINE

#### Cleaning Stages

**Stage 1: HTML Cleanup**
```
Remove Unwanted Elements:
├── JavaScript code blocks
├── CSS style blocks
├── HTML comments
├── Navigation elements (breadcrumbs, menus)
├── Advertisement divs
├── Social share buttons
├── Related articles sections
└── Footer/header boilerplate

Extract Clean Text:
├── Use BeautifulSoup .get_text()
├── Preserve paragraph structure
├── Keep meaningful whitespace
└── Extract alt text from images
```

**Stage 2: Text Normalization**
```
Normalization Steps:
├── Unicode normalization (NFKC form)
├── Remove control characters
├── Collapse multiple spaces to single space
├── Remove leading/trailing whitespace
├── Standardize quotes ("", '', ``)
├── Remove zero-width characters
├── Fix common encoding issues (Â, â€™)
└── Normalize line breaks (\r\n → \n)

Special Character Handling:
├── Keep currency symbols (Rs., $, €)
├── Keep percentages
├── Keep dates/times
└── Remove emoji for text analysis (keep in original)
```

**Stage 3: Content Extraction**
```
Extract Structured Information:
├── Headline extraction (H1, og:title)
├── Subheadline (H2, first paragraph)
├── Main body text
├── Pull quotes (blockquote tags)
├── Image captions
└── Byline information

Metadata Extraction:
├── Author name (from byline or meta)
├── Publication date (multiple format support)
├── Last modified date
├── Section/category
├── Tags/keywords
└── Related articles
```

**Stage 4: Language-Specific Processing**
```
Sinhala/Tamil Specific:
├── Unicode range validation
│   └── Sinhala: U+0D80–U+0DFF
│   └── Tamil: U+0B80–U+0BFF
├── Remove mixing of scripts (keep consistent)
├── Handle zero-width joiners correctly
└── Preserve diacritical marks

English Specific:
├── Fix common OCR errors
├── Expand contractions (it's → it is)
├── Standardize date formats
└── Fix title case where appropriate
```

---

## LANGUAGE DETECTION & TRANSLATION {#language-translation}

### 1.7 LANGUAGE DETECTION & TRANSLATION ENGINE

#### Language Detection

**Detection Strategy:**
```
Primary Method: langdetect library
    ↓
Confidence > 0.95? → Use detected language
    ↓ (No)
Fallback: fastText model
    ↓
Cross-validate both results
    ↓
If disagreement → Manual review queue
```

**Implementation Logic:**
```
detect_language(text):
    # Primary detection
    lang_detect_result = langdetect.detect_langs(text)
    primary_lang = lang_detect_result[0].lang
    primary_conf = lang_detect_result[0].prob
    
    # For Sri Lankan content
    If primary_lang in ['si', 'ta', 'en']:
        If primary_conf > 0.95:
            Return primary_lang, primary_conf
    
    # Fallback for low confidence
    fasttext_model = load_fasttext_model()
    secondary_lang, secondary_conf = fasttext_model.predict(text)
    
    # Cross-validation
    If primary_lang == secondary_lang:
        Return primary_lang, max(primary_conf, secondary_conf)
    Else:
        # Disagreement - log for review
        Log warning
        Return primary_lang, primary_conf, flag="needs_review"
```

#### Translation Pipeline

**When to Translate:**
```
Rules:
1. IF language is 'si' OR 'ta' → ALWAYS translate to 'en'
2. IF language is 'en' → No translation needed
3. IF language is mixed → Split by script, translate non-English parts
4. IF language unknown → Try translation, flag as uncertain
```

**Translation Architecture:**
```
TranslationEngine
├── Translation Methods (in priority order):
│   ├── 1. Cache Lookup (Redis)
│   ├── 2. Google Translate API (paid, high quality)
│   ├── 3. Facebook NLLB (free, good for Indic languages)
│   └── 4. Argos Translate (offline fallback)
│
├── Optimization:
│   ├── Batch translations (translate 10 articles at once)
│   ├── Cache common phrases
│   └── Translate in chunks (paragraphs, not full article)
│
└── Quality Assurance:
    ├── Back-translation validation
    ├── Confidence scoring
    └── Human review queue for critical content
```

**Translation Workflow:**
```
For article with language='si':
    
    1. Check Cache:
       text_hash = SHA256(sinhala_text)
       cached = Redis.get(f"translation:cache:{text_hash}")
       If cached: Return cached translation
    
    2. Perform Translation:
       translated_text = GoogleTranslateAPI.translate(
           text=sinhala_text,
           source='si',
           target='en'
       )
       translation_confidence = calculate_confidence(translated_text)
    
    3. Quality Check:
       back_translated = GoogleTranslateAPI.translate(
           text=translated_text,
           source='en',
           target='si'
       )
       similarity = calculate_similarity(sinhala_text, back_translated)
       
       If similarity < 0.7:
           Flag for review
           translation_confidence *= 0.5
    
    4. Cache Result:
       Redis.setex(
           f"translation:cache:{text_hash}",
           TTL=30_days,
           value=translated_text
       )
    
    5. Store in MongoDB:
       processed_articles.update({
           content.title_original: sinhala_text,
           content.title_english: translated_text,
           content.translation_confidence: translation_confidence
       })
```

**Cost Optimization Strategies:**
```
1. Translate Only Essential Parts:
   ├── Title: ALWAYS translate
   ├── First 3 paragraphs: ALWAYS translate
   └── Rest of body: CONDITIONALLY (based on importance)

2. Batch Processing:
   ├── Collect 50 articles
   ├── Send as batch to API
   └── Costs 70% less than individual calls

3. Smart Caching:
   ├── Common phrases cached indefinitely
   ├── Recent translations cached 30 days
   └── Cache hit rate target: >60%

4. Fallback to Free Services:
   ├── Use Google Translate for critical content
   ├── Use NLLB for bulk/background content
   └── Use Argos for non-critical offline processing
```

---

## DEDUPLICATION ENGINE {#deduplication}

### 1.8 DEDUPLICATION ENGINE

#### Deduplication Strategy (Multi-Level)

**Level 1: Exact URL Match (Fastest)**
```
Check: PostgreSQL article_metadata.url_hash
    ↓
If exact match found → Duplicate
    ↓
Return existing article_id
No further processing needed
```

**Level 2: Content Hash (Fast)**
```
Generate: MD5(normalized_title + first_200_chars)
    ↓
Check: Redis hash:content:{md5_hash}
    ↓
If match found → Likely duplicate
    ↓
Perform deeper similarity check
```

**Level 3: Semantic Similarity (Accurate but Slower)**
```
For articles that pass Level 1 & 2:
    ↓
Generate sentence embedding (SBERT)
    ↓
Compare with recent articles (last 48 hours)
    ↓
Calculate cosine similarity
    ↓
If similarity > 0.85 → Duplicate
If similarity 0.70-0.85 → Related (same story, different angle)
If similarity < 0.70 → Unique
```

#### Embedding Generation

**Purpose:** Convert text to vector for semantic comparison

**Implementation:**
```
Using Sentence-BERT:
    Model: all-MiniLM-L6-v2 (fast, good quality)
    Input: article.title + first_paragraph
    Output: 384-dimensional vector
    
Embedding Process:
    text_for_embedding = f"{title}. {first_paragraph}"
    embedding = model.encode(text_for_embedding)
    
Storage:
    MongoDB.processed_articles.embedding_vector = embedding
    
    OR (for faster similarity search):
    Use vector database like Faiss or pgvector
```

#### Similarity Calculation

**Cosine Similarity Formula:**
```
similarity = dot(embedding_A, embedding_B) / (norm(A) * norm(B))

Interpretation:
├── 1.00: Identical (should never happen with different articles)
├── 0.90-0.99: Exact duplicates
├── 0.80-0.89: Very similar (same event, minor differences)
├── 0.70-0.79: Related stories
└── <0.70: Different stories
```

**Deduplication Logic:**
```
For new_article:
    
    # Quick checks first
    If URL exists: Return "duplicate_exact"
    If content_hash exists: Mark "likely_duplicate", continue to verify
    
    # Semantic check
    embedding_new = generate_embedding(new_article)
    
    # Compare with articles from last 48 hours
    recent_articles = get_articles(last_48_hours=True)
    
    For each existing_article in recent_articles:
        similarity = cosine_similarity(embedding_new, existing_article.embedding)
        
        If similarity >= 0.90:
            # This is a duplicate
            new_article.is_duplicate = True
            new_article.duplicate_of = existing_article.article_id
            
            # Find the "best" version to keep
            If new_article.credibility_score > existing_article.credibility_score:
                # New article is from better source
                # Mark old as duplicate of new
                Swap relationship
            
            # Add to cluster
            Add both to duplicate_cluster
            Return "duplicate"
        
        Elif similarity >= 0.70:
            # Related story, not duplicate
            new_article.related_articles.append(existing_article.article_id)
            Mark as "related_story"
    
    # No duplicates found
    new_article.is_duplicate = False
    Return "unique"
```

#### Duplicate Cluster Management

**Purpose:** Track story evolution across sources and time

**Cluster Structure:**
```
DuplicateCluster:
    cluster_id: "fuel_crisis_2025_11_29_001"
    story_topic: "Fuel price increase announcement"
    
    articles: [
        {
            article_id: "ada_derana_001234",
            source: "Ada Derana",
            timestamp: "2025-11-29T10:00:00Z",
            credibility_score: 0.90,
            is_primary: True  # Best version
        },
        {
            article_id: "daily_mirror_005678",
            source: "Daily Mirror",
            timestamp: "2025-11-29T10:15:00Z",
            credibility_score: 0.85,
            is_primary: False
        },
        ...
    ]
    
    timeline: [
        {time: "10:00", event: "First reported by Ada Derana"},
        {time: "10:15", event: "Confirmed by Daily Mirror"},
        {time: "11:30", event: "Government statement published"}
    ]
    
    aggregate_sentiment: -0.42
    total_reach: 15000  # Combined from all sources
```

**Usage:**
- **For Layer 2**: Use primary article only (avoid counting same story multiple times)
- **For Story Evolution**: Track how narrative develops
- **For Source Credibility**: See who reported first, who reported accurately

---

## QUALITY ASSESSMENT & CREDIBILITY SCORING {#quality-assessment}

### 1.9 QUALITY ASSESSMENT & CREDIBILITY SCORING

#### Credibility Scoring Framework

**Multi-Factor Scoring:**
```
Final_Credibility_Score = 
    (Source_Base_Score × 0.40) +
    (Content_Quality_Score × 0.25) +
    (Cross_Verification_Score × 0.20) +
    (Author_Reputation_Score × 0.10) +
    (Timeliness_Score × 0.05)

Range: 0.00 to 1.00
```

**Factor 1: Source Base Score (Pre-assigned)**
```
Tier 1 Sources (0.85-1.00):
├── Government official sites
├── Central Bank publications
├── Established national newspapers
└── Verified international news agencies

Tier 2 Sources (0.65-0.84):
├── Regional newspapers
├── Business publications
├── Specialized news sites

Tier 3 Sources (0.40-0.64):
├── Blogs with verification
├── Aggregator sites
└── Social media verified accounts

Tier 4 Sources (0.00-0.39):
├── Unknown sources
├── Unverified social media
└── Questionable origins
```

**Factor 2: Content Quality Score**
```
Metrics:
├── Word count (longer = more detailed)
│   └── Scoring: sigmoid(word_count / 500)
│
├── Writing quality
│   ├── Grammar correctness
│   ├── Spelling errors
│   └── Sentence structure
│
├── Structure completeness
│   ├── Has headline: +0.1
│   ├── Has byline: +0.1
│   ├── Has timestamp: +0.1
│   ├── Has images: +0.05
│   └── Has sources cited: +0.15
│
└── Objectivity indicators
    ├── Low emotionalism: +0.15
    ├── Balanced language: +0.10
    └── Fact-based: +0.10

Max Score: 1.00
```

**Factor 3: Cross-Verification Score**
```
Check: How many other sources report this?

If reported by:
├── 5+ sources (0.80-1.00): Highly verified
├── 3-4 sources (0.60-0.79): Well verified
├── 2 sources (0.40-0.59): Partially verified
├── 1 source only (0.20-0.39): Unverified
└── 0 other sources (0.00-0.19): Single source claim

Bonus:
└── If high-credibility sources agree: +0.20
```

**Factor 4: Author Reputation** (Iteration 2)
```
Track authors over time:
├── Articles published
├── Accuracy rate (stories later proven true/false)
├── Awards/recognition
└── Specialization expertise

Build author_reputation table
Assign score: 0.00-1.00
```

**Factor 5: Timeliness Score**
```
Decay function:
├── 0-6 hours old: 1.00
├── 6-24 hours: 0.90
├── 1-3 days: 0.75
├── 3-7 days: 0.50
└── >7 days: 0.25

Reason: Recency matters for credibility in news
```

#### Bias Detection (Iteration 2 - Advanced)

**Bias Indicators:**
```
1. Language Analysis:
   ├── Emotional words density
   ├── Superlatives usage ("best", "worst", "shocking")
   ├── Loaded language ("regime" vs "government")
   └── One-sided presentation

2. Source Sentiment Patterns:
   ├── Track sentiment distribution per source
   ├── If consistently skewed → bias flag
   └── Example: Always negative about government

3. Missing Context:
   ├── Check if counterarguments presented
   ├── Check if multiple perspectives shown
   └── Quote diversity (not just one side)

Output:
├── bias_score: 0.00 (neutral) to 1.00 (highly biased)
├── bias_direction: "positive", "negative", "mixed"
└── bias_confidence: 0.00-1.00
```

---

## DATA PERSISTENCE & STORAGE PATTERNS {#data-persistence}

### 1.10 DATA PERSISTENCE & STORAGE PATTERNS

#### Write Patterns

**Pattern 1: Dual-Write (MongoDB + PostgreSQL)**
```
For each new article:
    
    # 1. Write to MongoDB (full content)
    mongodb_id = mongodb.raw_articles.insert_one({
        article_id: generated_id,
        source: {...},
        raw_content: {...},
        scrape_metadata: {...}
    })
    
    # 2. Write to PostgreSQL (metadata)
    postgres.article_metadata.insert({
        article_id: generated_id,
        source_id: source_id,
        url: url,
        url_hash: hash,
        published_at: timestamp,
        scraped_at: now(),
        processing_stage: 'raw'
    })
    
    # 3. If either fails, rollback both (transaction)
    # Use saga pattern or two-phase commit
```

**Pattern 2: Queue-Based Processing**
```
Scraper → MongoDB raw → Queue → Processor → MongoDB processed
                          ↓
                    PostgreSQL metadata updates
```

**Pattern 3: Batch Writes (For Performance)**
```
Accumulate 50 articles in memory
    ↓
Bulk insert to MongoDB (single operation)
    ↓
Bulk insert to PostgreSQL (single transaction)
    ↓
Benefits: 10x faster than individual inserts
```

#### Read Patterns

**Pattern 1: Hot Data from Redis**
```
Frequently accessed data:
├── Recent article IDs
├── Duplicate check cache
└── Real-time metrics

TTL Strategy:
├── Article seen flags: 48 hours
├── Translation cache: 30 days
├── Metrics: 1 hour
```

**Pattern 2: Metadata from PostgreSQL**
```
Use cases:
├── Find articles by date range
├── Get articles from specific source
├── Query by processing stage
└── Join with categories

Optimized with indexes
```

**Pattern 3: Full Content from MongoDB**
```
Use cases:
├── Feed to ML models
├── Display to users
├── Generate summaries
└── Export reports

Query by article_id (indexed)
```

#### Data Lifecycle Management

**Retention Policy:**
```
raw_articles (MongoDB):
├── Keep: 90 days
├── Archive: After 90 days to cold storage
└── Delete: After 1 year (or keep indefinitely if storage allows)

processed_articles (MongoDB):
├── Keep: Indefinitely (primary data)
└── Index: Last 90 days hot, older cold

article_metadata (PostgreSQL):
├── Keep: Indefinitely
└── Partition by month for performance

scrape_jobs (PostgreSQL):
├── Keep: 30 days
└── Archive: Aggregated statistics only

Redis:
├── Automatic TTL expiration
└── No manual cleanup needed
```

**Archival Strategy (Future):**
```
After 90 days:
├── Compress articles (gzip)
├── Move to S3/cloud storage
├── Keep metadata in PostgreSQL
└── On-demand retrieval if needed
```

---

## ITERATION 1 IMPLEMENTATION CHECKLIST {#iteration-1-checklist}

### Week 1 Deliverables - FOUNDATION

#### Day 1: Infrastructure Setup
```
□ Install & configure databases:
  □ PostgreSQL 14+
  □ MongoDB 6+
  □ Redis 7+
  □ TimescaleDB extension (if using)

□ Create database schemas:
  □ Run all CREATE TABLE scripts
  □ Create MongoDB collections
  □ Set up indexes
  □ Verify connections

□ Set up development environment:
  □ Python 3.10+ virtual environment
  □ Install core libraries:
    □ beautifulsoup4, lxml
    □ feedparser (for RSS)
    □ requests
    □ pymongo, psycopg2
    □ redis-py
    □ langdetect
    □ pyyaml (for configs)
  
□ Project structure:
  ├── /sources          (YAML configs)
  ├── /scrapers         (Scraper classes)
  ├── /pipeline         (Processing modules)
  ├── /models           (Database models)
  ├── /utils            (Helpers)
  └── /config           (Settings)
```

#### Day 2: Basic Scraper Framework
```
□ Implement configuration loader:
  □ YAML parser
  □ Config validator
  □ Source registry populator

□ Create 3 source configs:
  □ Ada Derana (RSS + HTML hybrid)
  □ Daily Mirror (RSS)
  □ News First (HTML)

□ Implement RSSFeedScraper:
  □ Fetch RSS feed
  □ Parse entries
  □ Extract fields
  □ Generate article_id
  □ Save to MongoDB
  
□ Test: Scrape 10 articles successfully
```

#### Day 3: Storage & Validation
```
□ Implement data models:
  □ MongoDB document classes
  □ PostgreSQL ORM models (SQLAlchemy)
  □ Data validation schemas

□ Implement validation pipeline:
  □ Required fields check
  □ Data type validation
  □ URL duplicate check (Redis)
  □ Basic quality filters

□ Implement dual-write pattern:
  □ MongoDB raw_articles
  □ PostgreSQL article_metadata
  □ Transaction handling

□ Test: 100% data integrity
```

#### Day 4: Cleaning & Language Processing
```
□ Implement cleaning pipeline:
  □ HTML stripping
  □ Text normalization
  □ Whitespace cleanup
  □ Special character handling

□ Implement language detection:
  □ langdetect integration
  □ Confidence scoring
  □ Language flagging

□ Implement basic translation:
  □ Google Translate API setup
  □ Translation function
  □ Cache mechanism (Redis)
  □ Error handling

□ Test: Clean 100 articles, translate 50
```

#### Day 5: Deduplication
```
□ Implement URL hash checking:
  □ SHA256 generation
  □ Redis cache lookup
  □ PostgreSQL fallback

□ Implement content similarity:
  □ Sentence-BERT setup
  □ Embedding generation
  □ Cosine similarity calculation
  □ Duplicate marking logic

□ Test: Identify duplicates in 200 articles
```

#### Day 6: Scheduling & Orchestration
```
□ Implement job scheduler:
  □ Cron-based triggering
  □ Priority queue (Redis)
  □ Job creation logic
  □ Adaptive frequency (basic)

□ Implement worker pool:
  □ Multi-threaded workers (5 workers)
  □ Job assignment
  □ Failure handling
  □ Retry logic

□ Test: Continuous scraping for 1 hour
```

#### Day 7: Monitoring & Integration Testing
```
□ Implement logging:
  □ Structured logging (JSON)
  □ Log levels (INFO, WARNING, ERROR)
  □ Log rotation
  □ Error tracking

□ Implement basic metrics:
  □ Articles scraped per source
  □ Success/failure rates
  □ Processing duration
  □ Storage to TimescaleDB

□ End-to-end test:
  □ Scrape from 3 sources
  □ Validate → Clean → Translate → Deduplicate
  □ Store in all databases
  □ Verify data flow

□ Documentation:
  □ Architecture diagram
  □ API documentation
  □ Setup guide
  □ Troubleshooting guide
```

---

## ITERATION 2: ADVANCED FEATURES (Days 8-14) {#iteration-2}

### Enhancements to Build

#### 2.1 Advanced Scrapers
```
□ Implement HTMLStaticScraper:
  □ Selector application engine
  □ Fallback mechanism
  □ Pagination handling
  □ Rate limiting

□ Implement APIScraper:
  □ Twitter API integration
  □ Generic REST API handler
  □ Authentication management
  □ Rate limit compliance

□ Add 5 more sources:
  □ 2 Sinhala news sites
  □ 1 Tamil news site
  □ 1 government data source
  □ 1 social media (Twitter trends)
```

#### 2.2 Enhanced Quality Control
```
□ Advanced bias detection:
  □ Sentiment pattern analysis
  □ Language bias indicators
  □ Source profiling
  □ Bias scoring

□ Content quality scoring:
  □ Grammar checking
  □ Writing quality metrics
  □ Structure completeness
  □ Objectivity assessment

□ Cross-verification system:
  □ Multi-source confirmation
  □ Fact-checking pipeline
  □ Credibility adjustment
```

#### 2.3 Social Media Processing
```
□ Twitter trend aggregation:
  □ Trending topics API
  □ Hashtag tracking
  □ Sentiment aggregation
  □ Geographic distribution

□ Facebook public page scraping:
  □ Page post collection
  □ Engagement metrics
  □ Comment sentiment
  □ Viral detection

□ Privacy compliance:
  □ No personal data storage
  □ Aggregation only
  □ Anonymization
  □ GDPR compliance
```

#### 2.4 Performance Optimization
```
□ Caching strategy:
  □ Multi-level caching
  □ Cache invalidation
  □ Cache hit monitoring
  □ TTL optimization

□ Database optimization:
  □ Index tuning
  □ Query optimization
  □ Connection pooling
  □ Read replicas

□ Parallel processing:
  □ Multi-process scrapers
  □ Distributed task queue
  □ Load balancing
  □ Resource management
```

#### 2.5 Advanced Deduplication
```
□ Story clustering:
  □ Topic modeling
  □ Cluster management
  □ Timeline generation
  □ Evolution tracking

□ Vector similarity search:
  □ Faiss integration OR
  □ pgvector extension
  □ Fast nearest neighbor search
  □ Batch similarity computation
```

#### 2.6 Monitoring & Observability
```
□ Dashboard for Layer 1:
  □ Real-time scraping status
  □ Source health metrics
  □ Error rates
  □ Processing pipeline visualization

□ Alerting system:
  □ Source failures
  □ Processing bottlenecks
  □ Quality degradation
  □ Anomaly detection

□ Performance monitoring:
  □ Response times
  □ Throughput metrics
  □ Resource utilization
  □ Bottleneck identification
```

---

## CRITICAL TECHNICAL SPECIFICATIONS {#technical-specs}

### Error Handling Strategy

```
Principle: Fail gracefully, retry intelligently, alert appropriately

Levels:
1. IGNORE: Minor issues (missing optional field)
2. LOG: Worth noting (translation confidence low)
3. RETRY: Temporary failures (network timeout)
4. ALERT: Serious issues (source down for 2 hours)
5. ABORT: Critical failures (database connection lost)

Retry Logic:
├── Attempt 1: Immediate
├── Attempt 2: Wait 60 seconds
├── Attempt 3: Wait 5 minutes
└── Attempt 4: Wait 30 minutes, then alert

Circuit Breaker:
If source fails 5 times in 30 minutes:
    → Stop scraping for 2 hours
    → Alert admin
    → Re-enable automatically
```

### Concurrency & Threading

```
Architecture: Multi-threaded workers with message queue

Components:
├── Main Scheduler (1 process)
│   └── Creates jobs every 15 minutes
│
├── Job Queue (Redis)
│   └── Holds pending jobs
│
├── Worker Pool (5-10 threads)
│   ├── Worker 1: Fetches job from queue
│   ├── Worker 2: Processes independently
│   └── Workers share nothing (stateless)
│
└── Result Aggregator (1 thread)
    └── Collects metrics, updates dashboards

Thread Safety:
├── Each worker has own database connection
├── No shared state between workers
├── Queue provides synchronization
└── Use locks only for critical sections
```

### API Rate Limiting

```
Strategy: Token bucket algorithm

Implementation:
For each source:
    bucket = Redis key: ratelimit:{source_id}
    capacity = source.max_requests_per_hour
    refill_rate = capacity / 60  # per minute
    
Before request:
    tokens = Redis.get(bucket)
    If tokens > 0:
        Redis.decr(bucket)
        Make request
    Else:
        Wait until tokens refilled
        Or skip this round

Refill:
    Every minute:
        Redis.incrby(bucket, refill_rate)
        Redis.expire(bucket, 3600)  # Reset hourly
```

### Data Validation Rules

```
Required Fields (ALL articles):
├── title: Length 10-500 chars
├── body: Length 50-50000 words
├── url: Valid URL format
├── publish_date: Parseable datetime
└── source_id: Exists in sources table

Optional but Recommended:
├── author
├── category
├── images
└── tags

Validation Severity:
├── BLOCKING: Missing required field → Reject
├── WARNING: Missing optional field → Accept with flag
└── INFO: Unusual but acceptable → Log only

Example:
If title.length < 10:
    Reject: "Title too short"
If body.word_count < 50:
    Reject: "Content too brief"
If publish_date > now():
    Reject: "Future publish date"
If publish_date < now() - 30 days:
    Warning: "Old article"
```

---

## INTEGRATION POINTS WITH LAYER 2 {#integration-layer2}

### Data Handoff Format

**What Layer 1 Provides to Layer 2:**
```
Processed Article Package:
{
    article_id: "unique_id",
    
    content: {
        title: "English title",
        body: "English full text",
        summary: "Optional 3-sentence summary"
    },
    
    metadata: {
        source: "Source name",
        source_credibility: 0.85,
        publish_timestamp: "ISO datetime",
        language_original: "si/ta/en",
        translation_confidence: 0.92
    },
    
    initial_classification: {
        source_category: "Economy",  # If source had one
        keywords: ["fuel", "price", "increase"],
        detected_language: "si"
    },
    
    quality: {
        credibility_score: 0.85,
        word_count: 450,
        is_duplicate: false,
        related_articles: ["id1", "id2"]
    },
    
    ready_for_ml: true  # Cleaned, translated, validated
}
```

**Storage Location:**
```
MongoDB: processed_articles collection
    ↓
Layer 2 queries for articles WHERE:
    - processing_pipeline.stages_completed includes 'translation'
    - processing_pipeline.ready_for_ml = true
    - processed_timestamp > last_layer2_run
```

**Query Interface:**
```
PostgreSQL View: layer2_ready_articles

CREATE VIEW layer2_ready_articles AS
SELECT 
    article_id,
    source_id,
    published_at,
    processing_stage,
    credibility_score
FROM article_metadata
WHERE 
    processing_stage = 'categorized'
    AND processed_at > NOW() - INTERVAL '1 hour'
ORDER BY published_at DESC;

Layer 2 queries this view
Then fetches full content from MongoDB
```

---

## DEPLOYMENT ARCHITECTURE {#deployment}

### Development Environment
```
Local Machine:
├── Docker Compose setup:
│   ├── PostgreSQL container
│   ├── MongoDB container
│   ├── Redis container
│   └── TimescaleDB container
│
├── Python application:
│   ├── Virtual environment
│   ├── Development dependencies
│   └── Hot reload enabled
│
└── Monitoring:
    ├── Logs to console
    └── Local dashboard (optional)
```

### Production Environment (Future)
```
Cloud Infrastructure:
├── Application Servers (2+):
│   ├── Load balanced
│   ├── Auto-scaling
│   └── Stateless workers
│
├── Database Cluster:
│   ├── PostgreSQL (primary + replica)
│   ├── MongoDB (replica set)
│   └── Redis (cluster mode)
│
├── Task Queue:
│   ├── Celery workers
│   ├── Redis as broker
│   └── Flower for monitoring
│
└── Monitoring:
    ├── Application metrics
    ├── Database metrics
    ├── Error tracking
    └── Alerting system
```

---

## TESTING STRATEGY {#testing}

### Unit Tests
```
Coverage: 80%+ of code

Test Categories:
├── Scraper functions
│   ├── RSS parsing
│   ├── HTML extraction
│   ├── Selector application
│   └── Error handling
│
├── Validation logic
│   ├── Field validation
│   ├── Data type checking
│   └── Quality filters
│
├── Processing pipelines
│   ├── Cleaning functions
│   ├── Translation
│   └── Deduplication
│
└── Database operations
    ├── CRUD operations
    ├── Transaction handling
    └── Query correctness
```

### Integration Tests
```
End-to-End Flows:
├── Scrape → Validate → Store → Retrieve
├── Multi-source scraping
├── Duplicate detection across sources
├── Translation pipeline
└── Queue processing

Test Data:
├── Sample articles (various languages)
├── Mock API responses
├── Known duplicate sets
└── Edge cases
```

### Performance Tests
```
Benchmarks:
├── Scraping speed: >100 articles/minute
├── Processing speed: >200 articles/minute
├── Database writes: >500 inserts/second
└── Deduplication: <1 second per article

Load Tests:
├── 10,000 articles in database
├── 100 concurrent scraping jobs
├── 1,000 articles/hour sustained
└── Resource usage monitoring
```

---

## SUCCESS METRICS FOR LAYER 1 {#success-metrics}

### Functional Metrics
```
□ Sources active: 10+
□ Articles per day: 500+
□ Languages supported: 3 (Sinhala, Tamil, English)
□ Duplicate detection accuracy: >95%
□ Translation quality: >0.85 confidence average
□ Data completeness: >90% articles have all required fields
```

### Performance Metrics
```
□ Scraping latency: <30 seconds per source
□ Processing latency: <5 seconds per article
□ Database write speed: >100 articles/minute
□ System uptime: >99%
□ Error rate: <1% of operations
```

### Quality Metrics
```
□ Credibility scoring accuracy: Validated by sampling
□ False duplicate rate: <5%
□ Translation accuracy: Spot-checked samples
□ Data validation: 100% articles pass basic validation
```

---

## FINAL ARCHITECTURE SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1 COMPLETE SYSTEM                   │
└─────────────────────────────────────────────────────────────┘

INPUT:                      OUTPUT TO LAYER 2:
├── 10+ news sources        ├── Cleaned articles
├── Social media trends     ├── Translated to English
├── Government data         ├── Deduplicated
└── Event streams           ├── Credibility scored
                            └── Ready for ML analysis

DATABASES:
├── PostgreSQL (Metadata, Configs, Relationships)
├── MongoDB (Content, Full-Text)
├── TimescaleDB (Metrics, Time-Series)
└── Redis (Cache, Queue, Locks)

PROCESSING PIPELINE:
Scrape → Validate → Clean → Detect Language → Translate → 
Deduplicate → Score Quality → Store → Ready for Layer 2

KEY FEATURES:
✓ Configuration-driven (add sources without code)
✓ Multi-language support (si/ta/en)
✓ Intelligent deduplication (semantic similarity)
✓ Quality assurance (credibility scoring)
✓ Scalable architecture (queue-based processing)
✓ Resilient (retry logic, error handling)
✓ Observable (logging, metrics, monitoring)
```

---

## APPENDIX: QUICK REFERENCE

### Essential Commands

**Database Setup:**
```bash
# PostgreSQL
createdb business_intel
psql business_intel < schemas/postgresql_schema.sql

# MongoDB
mongosh
use business_intel
db.createCollection("raw_articles")

# Redis
redis-cli PING
```

**Python Environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run Scraper:**
```bash
python -m scrapers.main --source ada_derana
python -m scrapers.scheduler  # Start continuous scraping
```

### Key File Locations
```
/sources/              - Source YAML configs
/scrapers/             - Scraper implementations
/pipeline/             - Processing modules
/config/settings.py    - Global configuration
/logs/                 - Application logs
/tests/                - Test suites
```

---

**End of Document**

This comprehensive blueprint provides everything needed to implement Layer 1 of your Business Intelligence Platform. Follow the iterative approach, starting with Iteration 1's foundation, and build systematically toward the advanced features in Iteration 2.
