# Layer 1 Scraping Enhancement Plan

## Current State Analysis

### Existing Infrastructure
- **Active Sites:** ada_derana, daily_ft, hiru_news (3 sources)
- **Inactive Placeholders:** daily_mirror, news_first, cbsl
- **Architecture:** ConfigurableScraper with JSONB selectors in database
- **Agentic Features:** 5 AI agents (Monitor, Processing, Priority, Validation, Scheduler)
- **LLM Integration:** Groq-based with fallbacks, content classification
- **Storage:** Multi-layer (PostgreSQL, MongoDB, Redis cache)
- **Smart Caching:** 70% performance improvement via ETag/content signatures

### Current Selector System
```json
{
  "list_url": "homepage URL",
  "article_link_pattern": "regex for article URLs",
  "article_link_selector": "CSS selector for links",
  "title": "h1 or title selector",
  "body": "article content container",
  "body_exclude": "ads, related content to exclude",
  "date": "publish date selector",
  "date_format": "strptime format",
  "author": "byline selector",
  "image": "image selector"
}
```

### Extraction Methods (3-tier fallback)
1. CSS selector (fastest, most reliable)
2. Regex pattern matching (flexible)
3. Heuristic fallback (NLP-based, handles unknown structures)

## Enhancement Strategy

### Phase 1: Expand News Coverage (Add 8+ Sites)

**Sri Lankan News:**
1. Daily Mirror (activate existing placeholder)
2. News First (activate existing placeholder)
3. Sunday Observer
4. The Island
5. Ceylon Today

**International News:**
6. BBC News - Asia
7. Reuters - Sri Lanka
8. Al Jazeera - Asia

### Phase 2: Government & Official Sources (Add 5+ Sites)

**Economic/Financial:**
1. Central Bank of Sri Lanka (activate placeholder)
2. Department of Census & Statistics
3. Ministry of Finance

**Policy/Administrative:**
4. Government Information Department
5. Parliament of Sri Lanka

### Phase 3: Specialized Sources (Add 3+ Sites)

**Think Tanks/Research:**
1. Institute of Policy Studies (IPS)
2. Verité Research

**Trade/Business:**
3. Ceylon Chamber of Commerce

## Technical Enhancements

### 1. Advanced Selector Features

**Multi-Path Selectors (fallback chains):**
```json
{
  "title": ["h1.article-title", "h1", "title", "meta[property='og:title']"]
}
```

**Attribute Extraction:**
```json
{
  "image": {
    "selector": "img.featured",
    "attribute": "data-src"  // for lazy-loaded images
  }
}
```

**Date Parsing Improvements:**
- Support multiple date formats per source
- Relative date parsing ("2 hours ago")
- ISO8601, RFC2822, custom formats

**Content Cleaning Enhancements:**
- Remove JavaScript/CSS blocks
- Strip tracking pixels
- Normalize whitespace
- Handle PDF/document links

### 2. Government Site Handling

**Special Features:**
- PDF extraction (reports, bulletins)
- Table data extraction (statistical data)
- Multi-page document handling
- Archive/historical data support

### 3. Agentic Framework Integration

**Enhanced Agent Capabilities:**
- **SourceMonitorAgent:** Auto-detect site structure changes
- **ProcessingAgent:** Enhanced entity extraction for government data
- **PriorityAgent:** Policy/economic indicator prioritization
- **ValidationAgent:** Cross-reference government statistics
- **SchedulerAgent:** Adaptive frequency based on update patterns

**LLM-Powered Features:**
- Auto-generate selectors for new sites (AI-based DOM analysis)
- Content classification (news/policy/economic/social)
- Entity extraction (organizations, policies, economic indicators)
- Sentiment analysis
- Topic modeling

### 4. Database Enhancements

**New Fields in SourceConfig:**
```python
content_type: str  # "article", "report", "statistics", "announcement"
document_formats: List[str]  # ["html", "pdf", "xlsx"]
extraction_complexity: str  # "simple", "moderate", "complex"
validation_rules: JSONB  # Quality checks specific to source
metadata_schema: JSONB  # Expected metadata fields
```

**Quality Metrics:**
- Extraction success rate per source
- Content completeness score
- Data freshness metrics
- Deduplication effectiveness

## Implementation Steps

### Step 1: Create Enhanced Source Configs (30 min)
- Define selectors for 15+ new sites
- Research site structures
- Test selector patterns

### Step 2: Enhance ConfigurableScraper (20 min)
- Add multi-path selector support
- Implement attribute extraction
- Add PDF/document handling
- Improve date parsing

### Step 3: Test & Validate (20 min)
- Test 5 representative sites
- Verify database storage
- Check data quality
- Monitor cache effectiveness

### Step 4: Integration Testing (15 min)
- Run full pipeline (Layer 1 → Layer 2)
- Verify agent integration
- Test LLM classification
- Check dashboard updates

## Success Metrics

**Quantitative:**
- Active sources: 3 → 18+ (6x increase)
- Government sources: 0 → 5+
- Extraction success rate: >85%
- Cache hit rate: >70%
- Average response time: <3s per article

**Qualitative:**
- Comprehensive news coverage
- Official statistics integration
- Policy document tracking
- Cross-source validation capability

## Risk Mitigation

**Site Structure Changes:**
- Implement change detection
- Alert on extraction failures
- Automatic fallback to heuristics

**Rate Limiting:**
- Respect robots.txt
- Implement per-source rate limits
- Distribute requests over time

**Data Quality:**
- Validation rules per source type
- Cross-reference verification
- Manual review queue for low-confidence extractions

## Timeline

- **Phase 1 (News):** 1 hour - Add 8 news sites, test 3
- **Phase 2 (Government):** 1 hour - Add 5 gov sites, test 2
- **Phase 3 (Specialized):** 30 min - Add 3 specialized sources
- **Testing:** 30 min - Full pipeline validation
- **Total:** ~3 hours for complete implementation

## Next Actions

1. Create `populate_enhanced_sources.py` with 15+ new configs
2. Enhance `configurable_scraper.py` with advanced features
3. Create `test_new_sources.py` for validation
4. Run end-to-end test with database verification
5. Update documentation
