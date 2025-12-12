# LAYER 1 AI AGENT SYSTEM - COMPREHENSIVE IMPLEMENTATION PLAN
## Intelligent Multi-Source Data Collection with Adaptive Processing

---

## EXECUTIVE SUMMARY

**Objective:** Enhance existing Layer 1 data collection system with AI agents that intelligently decide WHEN, WHAT, and HOW to scrape and process data from 26+ sources.

**Approach:** Add intelligent agent layer on top of existing scraping infrastructure - agents control existing tools, don't replace them.

**Technology Stack:**
- **Agent Framework:** LangChain + LangGraph
- **LLM Provider:** Groq (FREE - Llama 3.1 70B) with Together.ai fallback
- **Alternative:** OpenAI GPT-4/GPT-3.5 (if budget available)
- **Orchestration:** LangGraph state machine
- **Infrastructure:** Existing PostgreSQL + Redis + MongoDB

---

## SYSTEM ARCHITECTURE

### **High-Level Structure:**

```
┌──────────────────────────────────────────────────────────┐
│           AI AGENT ORCHESTRATION LAYER (NEW)             │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │   Master Orchestrator Agent (LangGraph)         │   │
│  └──────────────┬──────────────────────────────────┘   │
│                 │                                        │
│     ┌───────────┼───────────┐                          │
│     ↓           ↓           ↓                          │
│  ┌─────┐   ┌─────┐    ┌─────┐                         │
│  │Agent│   │Agent│    │Agent│                         │
│  │  1  │   │  2  │    │  3  │                         │
│  └──┬──┘   └──┬──┘    └──┬──┘                         │
│     │         │          │                             │
└─────┼─────────┼──────────┼──────────────────────────────┘
      │         │          │
      ↓         ↓          ↓
┌──────────────────────────────────────────────────────────┐
│        EXISTING LAYER 1 TOOLS (UNCHANGED)                │
│                                                          │
│  ├── scraper.py (BeautifulSoup/Scrapy)                 │
│  ├── pdf_processor.py (PyPDF2)                         │
│  ├── translator.py (Google Translate API)              │
│  ├── cleaner.py (Deduplication, normalization)         │
│  ├── database.py (PostgreSQL operations)               │
│  └── cache_manager.py (Redis)                          │
└──────────────────────────────────────────────────────────┘
      │
      ↓
┌──────────────────────────────────────────────────────────┐
│             EXISTING DATABASES (UNCHANGED)               │
│                                                          │
│  ├── PostgreSQL (structured data)                       │
│  ├── MongoDB (raw articles, PDFs)                       │
│  └── Redis (cache, job queue)                           │
└──────────────────────────────────────────────────────────┘
```

---

## PART 1: CORE AGENT DEFINITIONS

### **Agent 1: Source Monitor Agent**

**Purpose:** Intelligently decide WHEN to scrape each of 26+ sources based on their update patterns, priority, and resource availability.

**LLM Used:** Groq Llama 3.1 70B (FREE, excellent reasoning) - Alternative: GPT-4 if budget available

**Responsibilities:**
1. Monitor all 26 data sources continuously
2. Decide optimal scraping frequency per source (adaptive)
3. Detect breaking news signals requiring immediate scraping
4. Prioritize critical sources (DMC, weather alerts) over routine sources
5. Avoid redundant scraping (check last update time)
6. Handle scraper failures and trigger retries intelligently

**Tools This Agent Controls:**
- `check_last_scrape_time(source_name)` - Query database for last scrape timestamp
- `scrape_source(source_name)` - Execute existing scraper for specific source
- `check_breaking_signals()` - Query social media/alert systems for spikes
- `get_source_reliability(source_name)` - Get source quality score from database
- `update_scraping_schedule(source_name, new_frequency)` - Adjust frequency
- `log_scraping_decision(decision_data)` - Store decision reasoning

**Decision Logic Required:**
```
IF (time_since_last_scrape > source_typical_frequency AND no_breaking_news):
    Schedule normal scrape
ELIF (breaking_news_detected):
    Immediate scrape of ALL priority sources
ELIF (source_failed_last_time):
    Retry with exponential backoff
ELSE:
    Skip this cycle
```

**Key Instruction for Implementation:**
```
Create LangChain agent with GPT-4 that:
1. Has access to 6 tools listed above
2. Receives input: current_time, source_status_dict
3. Must OUTPUT: JSON with {source_name: "scrape"|"skip", reasoning: "..."}
4. Runs continuously in loop (every 60 seconds)
5. Logs all decisions to database for learning
```

---

### **Agent 2: Source-Specific Processing Agent**

**Purpose:** Intelligently process different source types (news, PDFs, APIs, social media) using appropriate methods.

**LLM Used:** Groq Llama 3.1 70B (FREE, fast classification) - Alternative: GPT-3.5-turbo if needed

**Responsibilities:**
1. Detect content type (news article, PDF document, API data, tweet, etc.)
2. Route to appropriate processor
3. Assess content quality and relevance
4. Decide if translation needed
5. Detect duplicates before processing
6. Extract metadata intelligently

**Tools This Agent Controls:**
- `detect_content_type(raw_content)` - Identify content format
- `process_news_article(content)` - Existing news processor
- `process_pdf_document(pdf_url)` - Existing PDF processor
- `process_api_data(json_data)` - Existing API processor
- `translate_content(text, source_lang)` - Existing translator
- `check_duplicate(content_hash)` - Check if already processed
- `calculate_quality_score(content)` - Assess article quality
- `extract_metadata(content)` - Pull out key info

**Decision Logic Required:**
```
content_type = detect_content_type(raw_data)

IF content_type == "pdf":
    processed = process_pdf_document(raw_data)
ELIF content_type == "news_article":
    IF language != "english":
        translated = translate_content(raw_data)
    processed = process_news_article(translated or raw_data)
ELIF content_type == "structured_data":
    processed = process_api_data(raw_data)

IF quality_score(processed) < 50:
    SKIP (low quality)
ELSE:
    STORE to database
```

**Key Instruction for Implementation:**
```
Create LangChain agent with GPT-3.5-turbo that:
1. Receives raw scraped content
2. Decides processing pipeline: detect type → translate? → process → quality check
3. Calls appropriate existing processor functions as tools
4. Returns processed data OR rejection with reason
5. Handles errors gracefully (retry with alternative method)
```

---

### **Agent 3: Priority & Alert Detection Agent**

**Purpose:** Rapidly identify critical/urgent content requiring immediate attention and fast-track processing.

**LLM Used:** Groq Llama 3.1 70B (FREE, accurate urgency assessment) - Alternative: GPT-4 for critical decisions

**Responsibilities:**
1. Scan all new content for urgency signals
2. Classify urgency level (critical/high/medium/low)
3. Detect disaster alerts, breaking news, policy changes
4. Route urgent items to fast-track processing
5. Trigger immediate notifications for critical alerts
6. Learn from past urgency classifications

**Tools This Agent Controls:**
- `scan_for_keywords(content, keyword_list)` - Search urgent keywords
- `classify_urgency(content)` - LLM-based urgency assessment
- `check_source_authority(source)` - Is this official/reliable source?
- `trigger_fast_track(content_id)` - Skip queue, process immediately
- `send_urgent_notification(alert_data)` - Alert system admins
- `log_urgency_decision(decision)` - Store for learning

**Urgency Classification Criteria:**
```
CRITICAL (process in <1 minute):
├── Disaster alerts (DMC)
├── Severe weather warnings
├── National emergencies
└── Major economic shocks

HIGH (process in <5 minutes):
├── Breaking political news
├── Large-scale strikes/protests
├── Policy announcements
└── Market crashes

MEDIUM (process in <15 minutes):
├── Important government circulars
├── Economic indicators
└── Industry news

LOW (process in normal queue):
├── Routine announcements
├── Historical data
└── Non-urgent updates
```

**Key Instruction for Implementation:**
```
Create LangChain agent with GPT-4 that:
1. Receives new content immediately after scraping
2. Performs urgency assessment in <10 seconds
3. Outputs urgency level + reasoning
4. If CRITICAL: trigger fast-track processing + notification
5. Stores classification for future learning
6. Uses few-shot prompting with examples of each urgency level
```

---

### **Agent 4: Data Quality & Validation Agent**

**Purpose:** Ensure data quality through intelligent validation, error detection, and correction.

**LLM Used:** Groq Llama 3.1 8B (FREE, fast pattern recognition) - Can also use Mixtral 8x7B

**Responsibilities:**
1. Validate scraped data completeness
2. Detect scraping errors or malformed content
3. Identify suspicious/fake content
4. Cross-validate information across sources
5. Suggest corrections for common errors
6. Flag content for human review when uncertain

**Tools This Agent Controls:**
- `check_required_fields(data_dict)` - Ensure all fields present
- `detect_scraping_errors(content)` - Find HTML artifacts, broken text
- `calculate_similarity(content1, content2)` - Cross-source validation
- `detect_fake_news_signals(content)` - Check for misinformation patterns
- `correct_common_errors(content)` - Fix known issues
- `flag_for_review(content_id, reason)` - Mark suspicious content

**Validation Rules:**
```
Required fields check:
├── title: must be non-empty, <200 chars
├── content: must be >100 chars
├── source: must be from whitelist
├── timestamp: must be valid datetime
└── url: must be valid URL

Quality checks:
├── No excessive special characters (>20%)
├── Proper sentence structure
├── Consistent language throughout
├── Source-appropriate content type
└── No HTML artifacts in text

Cross-validation:
├── IF major news: should appear in 2+ sources within 6 hours
├── IF policy change: should have government source confirmation
└── IF economic data: should match Central Bank if available
```

**Key Instruction for Implementation:**
```
Create LangChain agent with GPT-3.5-turbo that:
1. Receives processed content before storage
2. Runs validation checks in sequence
3. Outputs: {valid: true/false, quality_score: 0-100, issues: [...], suggestions: [...]}
4. If quality_score < 60: flag for review OR auto-correct if possible
5. Stores validation results in database
6. Learns from human review feedback
```

---

### **Agent 5: Adaptive Scheduler Agent**

**Purpose:** Dynamically adjust scraping frequencies based on source behavior patterns and system load.

**LLM Used:** Groq Llama 3.1 70B (FREE, strategic optimization) - Alternative: GPT-4 for complex optimization

**Responsibilities:**
1. Analyze historical scraping patterns per source
2. Detect source update frequency patterns
3. Optimize scraping schedule to minimize waste
4. Balance resource usage across sources
5. Adapt to changing source behavior
6. Generate efficiency reports

**Tools This Agent Controls:**
- `get_historical_scraping_data(source_name, days=30)` - Historical patterns
- `analyze_update_frequency(scraping_history)` - Detect patterns
- `calculate_optimal_frequency(source_analysis)` - Optimization algorithm
- `check_system_load()` - Current resource usage
- `update_global_schedule(new_schedule)` - Apply new frequencies
- `generate_efficiency_report()` - Performance metrics

**Optimization Logic:**
```
For each source:
1. Analyze past 30 days of scraping
2. Calculate: avg_articles_per_scrape, peak_hours, update_frequency
3. Determine optimal_scrape_frequency:
   - If avg_articles_per_scrape < 1: DECREASE frequency
   - If missing updates frequently: INCREASE frequency
   - If consistent patterns: align to peak hours
4. Apply constraints:
   - CRITICAL sources: min 5 min frequency
   - ROUTINE sources: max 4 hour frequency
   - TOTAL system load: <70% CPU, <80% memory
5. Implement new schedule gradually (A/B test)
```

**Key Instruction for Implementation:**
```
Create LangChain agent with GPT-4 that:
1. Runs daily analysis (not real-time)
2. Reviews all 26+ sources performance
3. Generates optimization recommendations
4. Outputs new schedule as JSON: {source: frequency_minutes}
5. Validates schedule doesn't exceed resource limits
6. Stores decisions with reasoning for review
7. Monitors impact of changes and auto-reverts if worse
```

---

## PART 2: MASTER ORCHESTRATOR (LangGraph)

### **Purpose:** Coordinate all 5 agents in optimal workflow sequence.

**Technology:** LangGraph (state machine for agent orchestration)

**LLM Used:** Groq Llama 3.1 70B (FREE, high-level coordination) - Alternative: GPT-4 for complex workflows

**Workflow State Machine:**

```python
# States in the workflow
class Layer1State:
    timestamp: datetime
    sources_to_scrape: List[str]
    scraped_content: List[dict]
    processed_articles: List[dict]
    validated_articles: List[dict]
    urgent_items: List[dict]
    status: str  # "monitoring" | "scraping" | "processing" | "validating" | "complete"
    
# Workflow nodes
NODES = [
    "monitor_sources",      # Agent 1: Decide what to scrape
    "scrape_data",          # Execute scraping (existing tools)
    "detect_urgency",       # Agent 3: Identify urgent items
    "process_content",      # Agent 2: Process each item
    "validate_quality",     # Agent 4: Quality checks
    "store_results"         # Store to database
]

# Conditional routing
IF urgent_items_detected:
    ROUTE urgent items to fast_track_processing
ELSE:
    CONTINUE normal_processing
```

**Key Instruction for Implementation:**
```
Build LangGraph workflow that:
1. Defines Layer1State as shared state across all agents
2. Creates nodes for each agent + scraping execution
3. Sets up edges:
   - monitor_sources → scrape_data
   - scrape_data → detect_urgency
   - detect_urgency → [fast_track OR normal_processing]
   - process_content → validate_quality
   - validate_quality → store_results
4. Runs continuously in loop (configurable interval)
5. Handles errors at each node (retry or skip)
6. Logs entire workflow execution to database
```

**Orchestrator Decision Points:**
```
1. START: Every 5 minutes
2. Monitor: Agent 1 decides which sources
3. Scrape: Execute for selected sources only
4. Triage: Agent 3 splits urgent vs normal
5. Process: 
   - Urgent: immediate, parallel processing
   - Normal: queue-based, batch processing
6. Validate: Agent 4 checks all
7. Store: Write to database
8. Optimize: Agent 5 reviews (daily)
```

---

## PART 3: INTEGRATION WITH EXISTING SYSTEM

### **Database Schema Additions:**

**New Tables Required:**

```sql
-- Agent decision logging
CREATE TABLE agent_decisions (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100),
    decision_type VARCHAR(50),
    input_data JSONB,
    output_decision JSONB,
    reasoning TEXT,
    llm_model VARCHAR(50),
    tokens_used INTEGER,
    latency_ms INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Scraping schedule (dynamic)
CREATE TABLE scraping_schedule (
    source_name VARCHAR(100) PRIMARY KEY,
    frequency_minutes INTEGER,
    last_scraped TIMESTAMP,
    last_articles_count INTEGER,
    priority_level VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Content urgency tracking
CREATE TABLE urgency_classifications (
    content_id INTEGER REFERENCES raw_articles(id),
    urgency_level VARCHAR(20),
    urgency_score FLOAT,
    detected_signals TEXT[],
    processing_priority INTEGER,
    classification_reasoning TEXT,
    classified_at TIMESTAMP DEFAULT NOW()
);

-- Quality validation results
CREATE TABLE quality_validations (
    content_id INTEGER REFERENCES raw_articles(id),
    is_valid BOOLEAN,
    quality_score FLOAT,
    validation_issues JSONB,
    auto_corrections JSONB,
    requires_review BOOLEAN,
    validated_at TIMESTAMP DEFAULT NOW()
);

-- Agent performance metrics
CREATE TABLE agent_metrics (
    agent_name VARCHAR(100),
    date DATE,
    decisions_made INTEGER,
    avg_latency_ms INTEGER,
    total_tokens_used INTEGER,
    success_rate FLOAT,
    cost_usd FLOAT
);
```

### **Existing Code Integration Points:**

**1. Wrap Existing Scrapers as Tools:**
```python
# scraper_tools.py - NEW FILE
from langchain.tools import Tool
from existing_scrapers import (
    scrape_daily_mirror,
    scrape_hiru_news,
    scrape_government_site,
    # ... all existing scrapers
)

# Convert each scraper to LangChain tool
SCRAPER_TOOLS = [
    Tool(
        name="scrape_daily_mirror",
        func=scrape_daily_mirror,  # Your existing function
        description="Scrape Daily Mirror news website. Returns list of articles."
    ),
    Tool(
        name="scrape_hiru_news",
        func=scrape_hiru_news,
        description="Scrape Hiru News website. Returns list of articles."
    ),
    # ... repeat for all 26+ sources
]
```

**2. Wrap Existing Processors as Tools:**
```python
# processor_tools.py - NEW FILE
from langchain.tools import Tool
from existing_processors import (
    translate_text,
    extract_pdf_text,
    clean_html,
    detect_language,
    # ... all existing processors
)

PROCESSOR_TOOLS = [
    Tool(
        name="translate_sinhala_to_english",
        func=lambda text: translate_text(text, "si", "en"),
        description="Translate Sinhala text to English"
    ),
    Tool(
        name="extract_pdf",
        func=extract_pdf_text,
        description="Extract text from PDF URL"
    ),
    # ... etc
]
```

**3. Database Access Tools:**
```python
# database_tools.py - NEW FILE
from langchain.tools import Tool
from existing_database import db_connection

def check_last_scrape(source_name: str) -> dict:
    """Query database for last scrape time"""
    query = "SELECT last_scraped, last_articles_count FROM scraping_schedule WHERE source_name = %s"
    result = db_connection.execute(query, (source_name,))
    return {"last_scraped": result[0], "count": result[1]}

DB_TOOLS = [
    Tool(
        name="check_last_scrape_time",
        func=check_last_scrape,
        description="Check when a source was last scraped and how many articles found"
    ),
    # ... more database tools
]
```

---

## PART 4: LLM CONFIGURATION & MANAGEMENT

### **LLM Selection Strategy:**

**Primary Model: Groq Llama 3.1 70B (FREE)** ⭐ RECOMMENDED
- Use for: All agents (Agent 1-5), Orchestrator
- Reason: FREE tier with 14,400 requests/day, fast inference, excellent quality
- Cost: **$0/month** for competition usage
- Speed: **Fastest** (tokens/second: ~750)
- Quality: ~85-90% of GPT-4 performance
- Temperature: 0.2 (consistent decisions)
- API: Compatible with LangChain

**Secondary Model: Groq Llama 3.1 8B (FREE)**
- Use for: Simple classification, validation tasks
- Reason: Even faster, sufficient for basic tasks
- Cost: **$0/month**
- Speed: **Ultra-fast** (tokens/second: ~1200)
- Temperature: 0.1 (very consistent)

**Fallback Model: Together.ai Llama 3.1 70B**
- Use when: Groq rate limited or unavailable
- Reason: $25 free credits = ~2 months free usage
- Cost: **FREE for 1-2 months**, then $0.20 per 1M tokens
- Quality: Same as Groq (same model)

**Alternative (If Budget Available): OpenAI GPT-4**
- Use for: Production after competition (if you want absolute best)
- Cost: ~$10 per 1M input tokens, $30 per 1M output tokens
- Quality: Slightly better (~10-15%) than Llama 3.1 70B
- Only use if FREE options insufficient

### **LLM API Configuration:**

```python
# llm_config.py - UPDATED FOR GROQ

from langchain_groq import ChatGroq
from langchain_community.llms import Together
from langchain_openai import ChatOpenAI  # Optional fallback
import os

# === PRIMARY: GROQ (FREE) ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Get free key from console.groq.com

# Model instances for different tasks
groq_llama_70b = ChatGroq(
    model="llama-3.1-70b-versatile",  # Main model - strategic decisions
    temperature=0.2,
    max_tokens=2000,
    api_key=GROQ_API_KEY,
    request_timeout=30
)

groq_llama_8b = ChatGroq(
    model="llama-3.1-8b-instant",  # Fast model - simple tasks
    temperature=0.1,
    max_tokens=1000,
    api_key=GROQ_API_KEY,
    request_timeout=20
)

groq_mixtral = ChatGroq(
    model="mixtral-8x7b-32768",  # Alternative model
    temperature=0.2,
    max_tokens=2000,
    api_key=GROQ_API_KEY,
    request_timeout=30
)

# === FALLBACK: TOGETHER.AI (FREE CREDITS) ===
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # Get from api.together.xyz

together_llama_70b = Together(
    model="meta-llama/Llama-3.1-70B-Instruct-Turbo",
    temperature=0.2,
    max_tokens=2000,
    together_api_key=TOGETHER_API_KEY
)

# === OPTIONAL: OPENAI (PAID) ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Only if budget available

gpt4_optional = ChatOpenAI(
    model="gpt-4",
    temperature=0.2,
    max_tokens=1000,
    api_key=OPENAI_API_KEY,
    request_timeout=30
)

gpt35_optional = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.1,
    max_tokens=1000,
    api_key=OPENAI_API_KEY,
    request_timeout=20
)

# === SMART MODEL SELECTOR ===
class ModelSelector:
    """Automatically select best available model with fallback"""
    
    def __init__(self):
        self.primary = groq_llama_70b
        self.fast = groq_llama_8b
        self.fallback = together_llama_70b
        self.premium = gpt4_optional if OPENAI_API_KEY else None
        
        self.groq_requests_today = 0
        self.groq_daily_limit = 14400
    
    def get_model(self, task_complexity: str = "medium"):
        """
        Get best model based on task complexity and availability
        
        task_complexity: "simple" | "medium" | "complex"
        """
        
        # Check Groq rate limit
        if self.groq_requests_today >= self.groq_daily_limit:
            print("Groq rate limit reached, using Together.ai fallback")
            return self.fallback
        
        # Select based on complexity
        if task_complexity == "simple":
            # Simple tasks: Use fastest free model
            return self.fast
        
        elif task_complexity == "medium":
            # Medium tasks: Use main free model
            return self.primary
        
        elif task_complexity == "complex":
            # Complex tasks: Use premium if available, else main
            return self.premium if self.premium else self.primary
        
        # Default
        return self.primary
    
    def track_request(self):
        """Track Groq usage"""
        self.groq_requests_today += 1

# Global model selector
model_selector = ModelSelector()

# === COST TRACKING (Updated for FREE models) ===
class CostTracker:
    """Track API costs - mostly $0 with Groq!"""
    
    def __init__(self):
        self.total_requests = 0
        self.groq_requests = 0
        self.together_requests = 0
        self.openai_requests = 0
        self.total_cost = 0.0
    
    async def track_call(self, llm, llm_func, *args, **kwargs):
        """Wrap LLM call to track usage"""
        
        result = await llm_func(*args, **kwargs)
        
        # Track by provider
        if isinstance(llm, ChatGroq):
            self.groq_requests += 1
            cost = 0.0  # FREE!
        elif isinstance(llm, Together):
            self.together_requests += 1
            cost = 0.0  # FREE credits
        elif isinstance(llm, ChatOpenAI):
            self.openai_requests += 1
            # Calculate OpenAI cost if used
            tokens = getattr(result, 'usage', {}).get('total_tokens', 0)
            cost = tokens * 0.00001  # Approximate
        
        self.total_requests += 1
        self.total_cost += cost
        
        # Log to database
        log_llm_usage(
            provider=llm.__class__.__name__,
            model=llm.model_name,
            tokens=getattr(result, 'usage', {}).get('total_tokens', 0),
            cost=cost
        )
        
        return result
    
    def get_daily_summary(self):
        """Daily usage summary"""
        return {
            "total_requests": self.total_requests,
            "groq_requests": self.groq_requests,
            "together_requests": self.together_requests,
            "openai_requests": self.openai_requests,
            "total_cost_usd": self.total_cost,
            "groq_limit_remaining": 14400 - self.groq_requests
        }

# Global cost tracker
cost_tracker = CostTracker()
```

### **Getting FREE API Keys:**

**1. Groq (PRIMARY - RECOMMENDED):**
```
1. Visit: https://console.groq.com
2. Sign up (free account)
3. Go to API Keys section
4. Create new API key
5. Copy key to .env file

FREE TIER:
├── 14,400 requests per day
├── Rate limit: 30 requests/minute
├── Context window: 8K tokens (Llama 3.1 70B)
└── NO CREDIT CARD REQUIRED
```

**2. Together.ai (FALLBACK):**
```
1. Visit: https://api.together.xyz
2. Sign up
3. Get $25 free credits (no card required)
4. Generate API key

FREE CREDITS:
├── $25 = ~125 million tokens
├── Llama 3.1 70B: $0.20 per 1M tokens
├── Lasts 1-2 months for your usage
└── Then pay-as-you-go (cheap)
```

**3. OpenAI (OPTIONAL):**
```
Only if you want premium quality
Costs ~$50-200/month depending on usage
Not needed for competition
```

### **Recommended Model Mapping:**

```python
# Which model for which agent

AGENT_MODEL_MAPPING = {
    "source_monitor": groq_llama_70b,      # Needs reasoning - use 70B
    "processing": groq_llama_8b,           # Simple classification - use 8B (faster)
    "priority_detection": groq_llama_70b,  # Accuracy critical - use 70B
    "validation": groq_llama_8b,           # Pattern recognition - use 8B
    "scheduler": groq_llama_70b,           # Strategic planning - use 70B
    "orchestrator": groq_llama_70b         # Coordination - use 70B
}

# Total daily usage estimate:
# - 5 agents × 4 cycles/hour × 24 hours = 480 agent calls/day
# - Well within 14,400 request limit!
```

### **Prompt Engineering Guidelines:**

**System Prompts Structure:**
```
All agent prompts should follow this template:

"""
You are a [AGENT_TYPE] agent for Sri Lankan business intelligence system.

ROLE: [Specific responsibility]

CONTEXT:
- Operating in Sri Lanka market
- Processing news/government/social data
- Time-sensitive decision making required

AVAILABLE TOOLS:
[List of tools with descriptions]

DECISION CRITERIA:
[Specific rules for this agent]

OUTPUT FORMAT:
[Expected JSON schema]

REASONING REQUIREMENT:
Always explain your decision in 1-2 sentences.

CONSTRAINTS:
- Respond within 10 seconds
- Use tools efficiently
- Prioritize accuracy over speed (except for urgent items)
"""
```

**Example for Source Monitor Agent:**
```python
SOURCE_MONITOR_PROMPT = """
You are a Source Monitoring Agent for a real-time business intelligence platform.

ROLE: Decide which news/government/social sources to scrape right now based on patterns, urgency signals, and resource efficiency.

CONTEXT:
- You monitor 26 different sources (news, government, social, financial)
- Some sources update every 5 minutes (breaking news sites)
- Some update once daily (government reports)
- You must balance thoroughness with resource efficiency
- Critical alerts (disasters, emergencies) require immediate scraping

AVAILABLE TOOLS:
1. check_last_scrape_time(source_name) - Get last scrape timestamp
2. scrape_source(source_name) - Execute scraping
3. check_breaking_signals() - Detect unusual activity
4. get_source_reliability(source_name) - Source quality score

DECISION CRITERIA:

SCRAPE NOW if:
├── Breaking news signals detected (scrape ALL priority sources)
├── Time since last scrape > typical frequency for that source
├── Source is critical (DMC, Weather) and >5 min since last scrape
└── Source failed last time (retry with exponential backoff)

SKIP if:
├── Scraped recently (within source's typical frequency)
├── Source offline/maintenance
└── System under heavy load AND source is low priority

PRIORITY LEVELS:
1. CRITICAL: DMC, Weather alerts, Breaking news (scrape every 5 min)
2. HIGH: Major news sites, Government (every 15 min)
3. MEDIUM: Provincial councils, Industry news (every 1 hour)
4. LOW: Research papers, Historical data (daily)

OUTPUT FORMAT:
{
  "sources_to_scrape": ["source1", "source2"],
  "sources_to_skip": ["source3"],
  "reasoning": "Brief explanation of decisions",
  "urgency_detected": true/false,
  "estimated_time_minutes": 5
}

Execute your analysis and make scraping decisions.
"""
```

### **Token Management:**

```python
# token_manager.py - NEW FILE

class TokenManager:
    """Manage token usage and costs"""
    
    def __init__(self, daily_budget_usd=50.0):
        self.daily_budget = daily_budget_usd
        self.daily_usage = 0.0
        self.token_costs = {
            "gpt-4": {"input": 0.00001, "output": 0.00003},  # per token
            "gpt-3.5-turbo": {"input": 0.0000005, "output": 0.0000015}
        }
    
    def can_make_call(self, estimated_tokens: int, model: str) -> bool:
        """Check if we're within budget"""
        estimated_cost = estimated_tokens * self.token_costs[model]["input"]
        return (self.daily_usage + estimated_cost) < self.daily_budget
    
    def optimize_prompt(self, prompt: str, max_tokens: int = 2000) -> str:
        """Trim prompt if too long"""
        # Simple token estimation: ~4 chars per token
        estimated_tokens = len(prompt) / 4
        
        if estimated_tokens > max_tokens:
            # Trim to fit
            return prompt[:max_tokens * 4]
        return prompt
```

---

## PART 5: DEPLOYMENT & EXECUTION

### **Directory Structure:**

```
layer1_ai_agents/
├── agents/
│   ├── __init__.py
│   ├── source_monitor_agent.py      # Agent 1
│   ├── processing_agent.py          # Agent 2
│   ├── priority_agent.py            # Agent 3
│   ├── validation_agent.py          # Agent 4
│   └── scheduler_agent.py           # Agent 5
│
├── orchestrator/
│   ├── __init__.py
│   ├── master_orchestrator.py       # LangGraph workflow
│   └── state_manager.py             # State management
│
├── tools/
│   ├── __init__.py
│   ├── scraper_tools.py             # Wrap existing scrapers
│   ├── processor_tools.py           # Wrap existing processors
│   └── database_tools.py            # Database operations
│
├── config/
│   ├── llm_config.py                # LLM settings
│   ├── source_config.py             # 26+ source definitions
│   └── agent_prompts.py             # All agent prompts
│
├── utils/
│   ├── cost_tracker.py              # Track API costs
│   ├── token_manager.py             # Manage token usage
│   └── logger.py                    # Logging utilities
│
├── existing_layer1/                 # Your current Layer 1
│   ├── scrapers/                    # UNCHANGED
│   ├── processors/                  # UNCHANGED
│   └── database/                    # UNCHANGED
│
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
└── README.md                        # Documentation
```

### **Dependencies (requirements.txt):**

```
# Core LangChain
langchain==0.1.0
langchain-openai==0.0.5  # Optional - only if using OpenAI
langgraph==0.0.20
langsmith==0.0.77

# LLM Providers (FREE)
langchain-groq==0.0.1  # PRIMARY - FREE
langchain-together==0.0.1  # FALLBACK - FREE credits

# LLM Providers (OPTIONAL - PAID)
openai==1.10.0  # Only if budget available

# Database
psycopg2-binary==2.9.9
redis==5.0.1
pymongo==4.6.1

# Existing dependencies (keep all)
beautifulsoup4
scrapy
requests
pandas
# ... all your current requirements
```

### **Environment Variables:**

```bash
# .env file

# === LLM API Keys (FREE PROVIDERS) ===
GROQ_API_KEY=gsk_...your-groq-key...  # Get from console.groq.com (FREE)
TOGETHER_API_KEY=...your-together-key...  # Get from api.together.xyz (FREE $25 credits)

# === Optional: OpenAI (PAID) ===
# OPENAI_API_KEY=sk-...your-key...  # Only if you want premium quality

# Database connections (existing)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bi_platform
POSTGRES_USER=admin
POSTGRES_PASSWORD=...

REDIS_HOST=localhost
REDIS_PORT=6379

MONGODB_URI=mongodb://localhost:27017/bi_platform

# Agent configuration
AGENT_MODE=production  # or "development"
LOG_LEVEL=INFO
ENABLE_COST_TRACKING=true
USE_GROQ_PRIMARY=true  # Use Groq as primary (FREE)
DAILY_BUDGET_USD=0.0  # Set to 0 for free tier, or budget if using paid APIs

# LangSmith (optional monitoring - also FREE tier available)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...  # Get from smith.langchain.com (FREE tier)
LANGCHAIN_PROJECT=layer1-agents
```

### **Setting Up FREE API Keys (DETAILED):**

**STEP 1: Get Groq API Key (PRIMARY - 5 minutes)**

```bash
# 1. Visit Groq Console
https://console.groq.com

# 2. Sign up with email (no credit card needed)
- Click "Sign Up"
- Enter email and password
- Verify email

# 3. Create API Key
- Go to "API Keys" section
- Click "Create API Key"
- Name it: "layer1-agents"
- Copy the key (starts with gsk_)

# 4. Add to .env file
GROQ_API_KEY=gsk_your_actual_key_here

# 5. Test it
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b-versatile",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Should return: AI response (means it's working!)
```

**STEP 2: Get Together.ai API Key (FALLBACK - 5 minutes)**

```bash
# 1. Visit Together.ai
https://api.together.xyz/signup

# 2. Sign up (free account)
- Enter email
- Verify email
- No credit card needed for $25 free credits

# 3. Generate API Key
- Go to "API Keys"
- Click "Create API Key"
- Copy the key

# 4. Add to .env file
TOGETHER_API_KEY=your_together_key_here

# 5. Check free credits
https://api.together.xyz/settings/billing
# Should show: $25.00 available
```

**STEP 3: Install Required Packages**

```bash
# Install LangChain Groq integration
pip install langchain-groq

# Install Together.ai integration
pip install langchain-together

# Optional: OpenAI (if you want paid option)
pip install langchain-openai openai
```

**STEP 4: Test Your Setup**

```python
# test_llm_setup.py

from langchain_groq import ChatGroq
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Test Groq
groq_key = os.getenv("GROQ_API_KEY")
print(f"Groq API Key loaded: {groq_key[:20]}...")

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    api_key=groq_key,
    temperature=0.2
)

response = llm.invoke("Say 'Groq is working!' if you can read this.")
print(f"Groq Response: {response.content}")

# Should print: "Groq is working!" or similar

print("✅ FREE LLM setup successful!")
print(f"Daily limit: 14,400 requests")
print(f"Cost: $0.00")
```

### **Main Execution Script:**

```python
# main.py

import asyncio
from orchestrator.master_orchestrator import MasterOrchestrator
from utils.logger import setup_logger

logger = setup_logger()

async def main():
    """Main entry point for AI agent system"""
    
    logger.info("Initializing Layer 1 AI Agent System...")
    
    # Initialize orchestrator
    orchestrator = MasterOrchestrator()
    
    logger.info("Starting continuous monitoring loop...")
    
    # Run indefinitely
    while True:
        try:
            # Execute one complete cycle
            result = await orchestrator.run_cycle()
            
            logger.info(f"Cycle complete. Status: {result['status']}")
            logger.info(f"Sources scraped: {len(result['sources_scraped'])}")
            logger.info(f"Articles processed: {len(result['articles_processed'])}")
            
            # Wait before next cycle (configurable)
            await asyncio.sleep(300)  # 5 minutes
            
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            await asyncio.sleep(60)  # Wait 1 min before retry

if __name__ == "__main__":
    asyncio.run(main())
```

---

## PART 6: IMPLEMENTATION INSTRUCTIONS FOR CLAUDE CODE

### **Step-by-Step Build Instructions:**

**PHASE 1: Setup & Integration (Day 1)**

```
INSTRUCTION 1: Project Setup
├── Create directory structure as shown above
├── Install dependencies from requirements.txt
├── Set up environment variables in .env
└── Test database connections

INSTRUCTION 2: Wrap Existing Tools
├── Create scraper_tools.py:
│   └── Convert each existing scraper function into LangChain Tool
├── Create processor_tools.py:
│   └── Convert each processor into Tool
└── Create database_tools.py:
    └── Create tools for database queries

INSTRUCTION 3: Database Schema
├── Create new tables: agent_decisions, scraping_schedule, urgency_classifications, quality_validations, agent_metrics
├── Add indexes for performance
└── Migrate existing data if needed
```

**PHASE 2: Build Individual Agents (Day 2-3)**

```
INSTRUCTION 4: Source Monitor Agent (Agent 1)
File: agents/source_monitor_agent.py

Requirements:
├── Use GPT-4 model
├── Initialize with 6 tools (check_last_scrape, scrape_source, etc.)
├── System prompt as defined in PART 4
├── Input: current_time, source_status (from database)
├── Output: JSON with sources to scrape + reasoning
├── Log all decisions to agent_decisions table
└── Handle errors gracefully (retry logic)

Key functions to implement:
- __init__(): Initialize agent with tools and prompt
- monitor_cycle(): Main decision-making loop
- _create_tools(): Define all 6 tools
- _execute_decision(): Execute scraping based on decision

INSTRUCTION 5: Processing Agent (Agent 2)
File: agents/processing_agent.py

Requirements:
├── Use GPT-3.5-turbo model
├── Initialize with 8 tools (detect_type, process_news, translate, etc.)
├── Input: raw_content (from scraper)
├── Output: processed_data (ready for database)
├── Route to correct processor based on content type
└── Handle translation if needed

Key functions:
- process_content(raw_content): Main entry point
- _detect_type(): Identify content format
- _route_to_processor(): Call appropriate processor
- _validate_output(): Check processed data quality

INSTRUCTION 6: Priority Detection Agent (Agent 3)
File: agents/priority_agent.py

Requirements:
├── Use GPT-4 model (accuracy critical)
├── Initialize with 6 tools (scan_keywords, classify_urgency, etc.)
├── Input: new_content (immediately after scraping)
├── Output: urgency_classification (critical/high/medium/low)
├── Must respond in <10 seconds
└── Trigger fast-track if critical

Key functions:
- detect_urgency(content): Main classification
- _check_critical_signals(): Look for disaster/emergency keywords
- _classify(): LLM-based urgency assessment
- _trigger_fast_track(): Route urgent items immediately

INSTRUCTION 7: Validation Agent (Agent 4)
File: agents/validation_agent.py

Requirements:
├── Use GPT-3.5-turbo model
├── Initialize with 6 tools (check_fields, detect_errors, etc.)
├── Input: processed_content (before storage)
├── Output: validation_result (valid/invalid + quality_score)
├── Auto-correct common errors when possible
└── Flag suspicious content for review

Key functions:
- validate(content): Main validation
- _check_required_fields(): Ensure completeness
- _calculate_quality_score(): 0-100 scoring
- _cross_validate(): Check against other sources

INSTRUCTION 8: Scheduler Agent (Agent 5)
File: agents/scheduler_agent.py

Requirements:
├── Use GPT-4 model (strategic optimization)
├── Initialize with 6 tools (get_history, analyze_frequency, etc.)
├── Input: historical_data (past 30 days)
├── Output: optimized_schedule (JSON with frequencies)
├── Runs daily (not real-time)
└── Validates resource constraints

Key functions:
- optimize_schedule(): Main optimization
- _analyze_patterns(): Detect source update patterns
- _calculate_optimal_frequency(): Optimization algorithm
- _validate_constraints(): Check resource limits
```

**PHASE 3: Build Orchestrator (Day 4)**

```
INSTRUCTION 9: Master Orchestrator
File: orchestrator/master_orchestrator.py

Requirements:
├── Use LangGraph for state machine
├── Define Layer1State schema
├── Create 6 workflow nodes
├── Set up conditional routing
└── Handle errors at each node

Workflow nodes:
1. monitor_sources: Call Agent 1 → Get scraping decisions
2. scrape_data: Execute scrapers for selected sources
3. detect_urgency: Call Agent 3 → Classify urgency
4. process_content: Call Agent 2 → Process all content
5. validate_quality: Call Agent 4 → Quality checks
6. store_results: Write to database

Conditional routing:
├── IF urgency == "critical": fast_track_processing
└── ELSE: normal_processing

Key functions:
- run_cycle(): Execute one complete workflow
- _monitor_sources(state): Agent 1 decision node
- _scrape_data(state): Execute scraping
- _detect_urgency(state): Agent 3 classification
- _process_content(state): Agent 2 processing
- _validate_quality(state): Agent 4 validation
- _store_results(state): Database storage

Error handling:
├── Retry failed nodes (max 3 attempts)
├── Log all errors to database
└── Continue workflow even if one node fails
```

**PHASE 4: Integration & Testing (Day 5)**

```
INSTRUCTION 10: Integration Testing

Test each agent independently:
├── Agent 1: Test with mock source_status data
├── Agent 2: Test with sample news article
├── Agent 3: Test with urgent vs non-urgent content
├── Agent 4: Test with valid and invalid data
└── Agent 5: Test with historical data

Test orchestrator:
├── Run one complete cycle manually
├── Verify state transitions
├── Check database writes
└── Validate error handling

Test integration with existing Layer 1:
├── Verify scrapers are called correctly
├── Check processors receive correct input
├── Validate database schema compatibility
└── Test end-to-end data flow

Performance testing:
├── Measure latency of each agent
├── Track token usage and costs
├── Monitor database query performance
└── Test under load (100+ articles)
```

**PHASE 5: Deployment (Day 6-7)**

```
INSTRUCTION 11: Production Deployment

Cloud deployment (Google Cloud):
├── Create VM instance (n1-standard-4)
├── Install dependencies
├── Configure environment variables
├── Set up systemd service for auto-restart
└── Configure logging and monitoring

Monitoring setup:
├── LangSmith dashboard for agent tracing
├── Database monitoring (query performance)
├── Cost tracking dashboard
└── Error alerting (email/SMS)

Documentation:
├── API documentation for each agent
├── Workflow diagrams
├── Troubleshooting guide
└── Cost optimization tips

Go-live checklist:
├── All tests passing
├── Database migrations complete
├── Monitoring configured
├── Backup strategy in place
├── Team trained on system
└── Rollback plan ready
```

---

## PART 7: MONITORING & OPTIMIZATION

### **Cost Monitoring:**

```python
# Monitor daily costs (mostly $0 with Groq!)
SELECT 
    DATE(timestamp) as date,
    agent_name,
    provider,
    SUM(tokens_used) as total_tokens,
    SUM(cost_usd) as total_cost  -- Should be $0 with Groq!
FROM agent_decisions
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY date, agent_name, provider
ORDER BY date DESC;

# Track Groq rate limit usage
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as groq_requests,
    14400 - COUNT(*) as remaining_requests
FROM agent_decisions
WHERE provider = 'ChatGroq'
AND DATE(timestamp) = CURRENT_DATE
GROUP BY date;

# Alert if approaching Groq daily limit
IF groq_requests > 12000:  -- 80% of 14,400
    SEND_ALERT("Approaching Groq daily limit - will fallback to Together.ai soon")

# Cost summary (should show $0 for Groq)
SELECT 
    provider,
    COUNT(*) as requests,
    SUM(cost_usd) as total_cost
FROM agent_decisions
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY provider;

-- Expected result:
-- ChatGroq: $0.00 (FREE)
-- Together: $0.00 (FREE credits)
-- ChatOpenAI: $X.XX (only if used)
```

### **Performance Metrics:**

```python
# Track agent performance
SELECT 
    agent_name,
    COUNT(*) as decisions_made,
    AVG(latency_ms) as avg_latency,
    AVG(tokens_used) as avg_tokens
FROM agent_decisions
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY agent_name;

# Identify bottlenecks
SELECT 
    agent_name,
    MAX(latency_ms) as max_latency
FROM agent_decisions
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY agent_name
HAVING MAX(latency_ms) > 30000;  -- Flag if >30 seconds
```

### **Quality Metrics:**

```python
# Validation accuracy
SELECT 
    DATE(validated_at) as date,
    AVG(quality_score) as avg_quality,
    SUM(CASE WHEN requires_review THEN 1 ELSE 0 END) as review_count
FROM quality_validations
GROUP BY date
ORDER BY date DESC;

# Urgency classification accuracy (requires human feedback)
SELECT 
    urgency_level,
    COUNT(*) as classifications,
    AVG(CASE WHEN human_confirmed THEN 1.0 ELSE 0.0 END) as accuracy
FROM urgency_classifications
WHERE human_feedback IS NOT NULL
GROUP BY urgency_level;
```

---

## PART 8: ERROR HANDLING & FALLBACKS

### **LLM Failures:**

```python
# Implement graceful degradation with FREE models

IF Groq unavailable OR rate limited:
    FALLBACK_TO Together.ai (also FREE)
    LOG "Using Together.ai fallback - Groq unavailable/rate limited"

IF Together.ai also unavailable:
    IF OpenAI configured:
        FALLBACK_TO GPT-3.5-turbo (PAID)
        LOG "Using paid OpenAI fallback - FREE providers unavailable"
    ELSE:
        FALLBACK_TO rule-based decisions
        LOG "All LLMs unavailable - using rule-based fallback"

IF approaching Groq daily limit (>13,000 requests):
    START_USING Together.ai to preserve Groq capacity
    LOG "Proactively switching to Together.ai to stay within limits"

# Rate limit specific handling
IF Groq rate limit error (30 req/min):
    WAIT 2 seconds
    RETRY with exponential backoff
    IF still failing after 3 retries:
        SWITCH_TO Together.ai

# Cost tracking
IF using OpenAI fallback:
    INCREMENT cost_alert_counter
    IF daily_cost > $10:
        ALERT "Unexpected paid API usage - investigate"
```

### **Agent Failures:**

```python
# Handle individual agent failures

IF Agent 1 (Monitor) fails:
    USE default scraping schedule (every 15 min for all)
    CONTINUE with other agents

IF Agent 2 (Processing) fails:
    STORE raw content without processing
    RETRY processing later

IF Agent 3 (Priority) fails:
    ASSUME medium urgency for all
    CONTINUE normal processing

IF Agent 4 (Validation) fails:
    SKIP validation (accept all)
    FLAG for manual review later

IF Agent 5 (Scheduler) fails:
    KEEP current schedule
    RETRY optimization next day
```

### **Database Failures:**

```python
# Database connection issues

IF PostgreSQL unavailable:
    QUEUE operations in Redis
    RETRY every 30 seconds
    ALERT if down >5 minutes

IF Redis unavailable:
    CONTINUE without caching
    PERFORMANCE degraded but functional

IF MongoDB unavailable:
    STORE raw content in PostgreSQL JSONB
    MIGRATE to MongoDB when available
```

---

## PART 9: EXAMPLE WORKFLOWS

### **Example 1: Normal Scraping Cycle**

```
TIME: 10:00 AM
STATUS: Normal operations

STEP 1: Monitor (Agent 1)
├── Query: "Which sources should I scrape now?"
├── Decision: 
│   ├── Daily Mirror: Last scraped 16 min ago → SCRAPE
│   ├── Hiru News: Last scraped 4 min ago → SKIP
│   ├── DMC: Last scraped 8 min ago → SCRAPE (critical)
│   └── Central Bank: Last scraped 2 hours ago → SCRAPE
├── Reasoning: "Daily Mirror past typical 15 min frequency, DMC is critical source"
└── Output: ["daily_mirror", "dmc", "central_bank"]

STEP 2: Scrape
├── Execute scrapers for 3 sources
├── Results: 
│   ├── Daily Mirror: 5 articles
│   ├── DMC: 1 alert
│   └── Central Bank: 1 data release
└── Total: 7 items

STEP 3: Priority Detection (Agent 3)
├── Scan all 7 items
├── Classifications:
│   ├── DMC alert: CRITICAL (flood warning)
│   ├── Daily Mirror political: MEDIUM
│   ├── Central Bank data: MEDIUM
│   └── Others: LOW
└── Fast-track: 1 item (DMC alert)

STEP 4: Processing
├── FAST TRACK (parallel):
│   └── DMC alert → Process immediately (30 seconds)
├── NORMAL QUEUE (sequential):
│   └── 6 items → Process batch (2 minutes)

STEP 5: Validation (Agent 4)
├── Check all 7 processed items
├── Results:
│   ├── 6 items: Valid (quality 85-95)
│   └── 1 item: Low quality (quality 45) → Flag for review

STEP 6: Storage
├── Write 6 valid items to database
├── Flag 1 item for manual review
└── Update scraping schedule

CYCLE COMPLETE
Time: 3 minutes
Cost: $0.00 (FREE with Groq!)
Articles processed: 6
Alerts generated: 1
Groq requests used: 7 (14,393 remaining today)
```

### **Example 2: Breaking News Event**

```
TIME: 2:30 PM
STATUS: Breaking news detected

STEP 1: Monitor (Agent 1)
├── breaking_signals() detects:
│   ├── Twitter: Spike in #LKA mentions (+500%)
│   ├── Social media: "protest" trending
│   └── Multiple keywords: "parliament", "strike"
├── Decision: URGENT MODE ACTIVATED
└── Action: Scrape ALL priority sources immediately

STEP 2: Scrape
├── 15 sources scraped simultaneously
├── Results: 43 new articles (unusual volume)
└── Time: 2 minutes (parallel execution)

STEP 3: Priority Detection (Agent 3)
├── Process all 43 articles urgently
├── Classifications:
│   ├── CRITICAL: 2 (major protest at parliament)
│   ├── HIGH: 8 (related developments)
│   ├── MEDIUM: 20
│   └── LOW: 13
└── Fast-track: 10 items

STEP 4: Processing
├── All 10 critical/high items processed in parallel
├── LLM extracts:
│   ├── Event: Large-scale protest
│   ├── Location: Colombo parliament
│   ├── Scale: 5000+ people
│   ├── Demands: Economic reforms
│   └── Status: Ongoing
└── Cross-validation: 5 sources confirm same event

STEP 5: Validation
├── High confidence (multi-source confirmation)
├── Quality scores: 90-95
└── All items validated

STEP 6: Immediate Actions
├── Store to database
├── TRIGGER URGENT ALERTS to all users
├── Update operational indicators (Layer 2)
└── Generate risk alerts (Layer 4)

STEP 7: Continued Monitoring
├── Switch to high-frequency mode
├── Scrape every 5 minutes until event resolves
└── Monitor for new developments

BREAKING NEWS CYCLE COMPLETE
Time: 8 minutes (detection to alert)
Cost: $0.00 (FREE with Groq!)
Articles processed: 43
Urgent alerts sent: 127 businesses affected
Groq requests used: 58 (14,342 remaining today)
```

---

## PART 10: SUCCESS METRICS

### **Key Performance Indicators:**

```
EFFICIENCY METRICS:
├── Scraping efficiency: % reduction in unnecessary scrapes (target: 40%)
├── Processing time: Average time from scrape to storage (target: <2 min)
├── Resource utilization: CPU/memory usage (target: <70%)
└── Cost per article: LLM cost divided by articles processed (target: <$0.02)

QUALITY METRICS:
├── Classification accuracy: % correct PESTEL categories (target: >90%)
├── Urgency accuracy: % correct urgency classifications (target: >85%)
├── Validation catch rate: % of bad data caught (target: >95%)
└── Duplicate detection: % duplicates prevented (target: >98%)

SPEED METRICS:
├── Critical alert latency: Time to process urgent items (target: <1 min)
├── Normal processing latency: Average processing time (target: <5 min)
├── System response time: End-to-end cycle time (target: <10 min)
└── Breaking news detection: Time to detect and scrape (target: <2 min)

COST METRICS:
├── Daily LLM cost: Total API usage (target: $0/day with Groq FREE tier)
├── Groq requests used: Track against 14,400 daily limit (target: <12,000/day)
├── Fallback usage: Together.ai or OpenAI usage (target: minimize)
├── Cost per insight: Should be $0 with FREE tier (target: $0)
└── Budget adherence: Stay FREE or within budget if using paid (target: 100%)
```

---

## FINAL CHECKLIST

```
PRE-DEPLOYMENT:
☐ All 5 agents built and tested individually
☐ LangGraph orchestrator working end-to-end
☐ Database schema updated and migrated
☐ All existing Layer 1 tools wrapped as LangChain tools
☐ LLM API keys configured and tested
☐ Cost tracking and monitoring enabled
☐ Error handling and fallbacks implemented
☐ Integration tests passing (>95% success rate)
☐ Performance benchmarks met
☐ Documentation complete

DEPLOYMENT:
☐ Cloud infrastructure provisioned
☐ Environment variables configured
☐ Databases accessible from cloud
☐ Monitoring dashboards set up
☐ Alerting configured (email/SMS)
☐ Backup and recovery tested
☐ Rollback plan documented
☐ Team trained on new system

POST-DEPLOYMENT:
☐ Monitor for 48 hours continuously
☐ Track costs daily
☐ Review agent decisions for quality
☐ Collect user feedback
☐ Optimize based on real usage
☐ Document lessons learned
```

---

## APPENDIX: QUICK REFERENCE

### **Agent Quick Reference:**

| Agent | Model | Purpose | Speed | Cost |
|-------|-------|---------|-------|------|
| Source Monitor | Groq Llama 70B | Scraping decisions | Fast | FREE ✅ |
| Processing | Groq Llama 8B | Route & process | Ultra-Fast | FREE ✅ |
| Priority Detection | Groq Llama 70B | Urgency classification | Fast | FREE ✅ |
| Validation | Groq Llama 8B | Quality checks | Ultra-Fast | FREE ✅ |
| Scheduler | Groq Llama 70B | Optimize frequencies | Fast | FREE ✅ |

**Alternative Models (if needed):**
- Together.ai Llama 70B - FREE credits fallback
- OpenAI GPT-4 - Paid premium option (~$$$ per month)
- OpenAI GPT-3.5 - Paid budget option (~$ per month)

### **Tool Categories:**

```
SCRAPING TOOLS (26+):
├── News sites (5)
├── Government (8)
├── Financial (3)
├── Social (3)
├── Infrastructure (5)
└── Other (2+)

PROCESSING TOOLS (8):
├── Language detection
├── Translation
├── PDF extraction
├── HTML cleaning
├── Metadata extraction
├── Duplicate detection
├── Quality scoring
└── Entity extraction

DATABASE TOOLS (6):
├── Query last scrape
├── Store articles
├── Check duplicates
├── Update schedule
├── Log decisions
└── Get metrics
```

---

**END OF IMPLEMENTATION PLAN**

This document provides complete instructions for building an AI agent-enhanced Layer 1 system. Follow instructions sequentially. Use Claude Code for implementation. Refer to chat history for additional context on existing Layer 1 architecture.
