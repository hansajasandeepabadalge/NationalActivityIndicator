# 🕷️ Universal Scraping Framework & Intelligent Deduplication — Full Analysis

> **Project:** National Activity Indicator  
> **Date:** 2026-04-08  
> **Scope:** All files related to scraping infrastructure and semantic deduplication

---

## Part 1 — Universal Scraping Framework

### 1.1 File Inventory

| File | Size | Role |
|---|---|---|
| `app/scrapers/base.py` | 74 lines | Abstract contract for all scrapers |
| `app/scrapers/configurable_scraper.py` | 624 lines | DB-driven universal scraper engine |
| `app/scrapers/news/ada_derana.py` | 129 lines | Site-specific hardcoded scraper |
| `app/agents/tools/scraper_tools.py` | 532 lines | LangChain tool wrappers + smart cache layer |
| `app/integration/pipeline.py` | 664 lines | End-to-end Layer2→Layer3→Layer4 orchestrator |
| `app/integration/adapters.py` | 22,849 bytes | Layer-to-layer data transformation adapters |
| `app/integration/contracts.py` | 9,429 bytes | Pydantic contracts for inter-layer data |

---

### 1.2 Architecture — How the Universal Scraper Works

```
DATABASE (source_configs table)
  └─ selectors JSONB: { list_url, article_link_selector, title, body, date, image, ... }
  └─ rate_limit_requests, rate_limit_period
  └─ scraper_class, is_active, requires_javascript
         │
         ▼
ConfigurableScraper.from_source_name(name)
  └─ SessionLocal() → db.query(SourceConfig) → get_selectors()
         │
         ▼
  [Rate Limit Check] ← _request_times sliding window (IN-MEMORY)
         │
         ▼
  httpx.AsyncClient.get(list_url)
         │
         ▼
  Link Extraction (3-level fallback):
    1. CSS selector:  soup.select(article_link_selector)
    2. Regex:         re.findall(article_link_pattern, html)
    3. Heuristic:     all <a> tags matching /news/, /article/ etc.
         │
         ▼
  [article_links[:20]]  ← HARDCODED CAP
         │
    For each link:
      [Rate Limit Check]
      httpx.AsyncClient.get(article_url)
      _extract_text(title_selector)
      _extract_body(body_selector, body_exclude)
      _extract_images(image_selector)
      _parse_date(date_selector, date_format)
      create_article() → RawArticle (Pydantic)
         │
         ▼
  List[RawArticle]
```

**Scraper Selection Logic in `scraper_tools.py`:**
```
get_scraper_instance(source_name)
  ├─ 1. Check SCRAPER_REGISTRY dict (hardcoded custom scrapers)
  │       └─ "ada_derana" → AdaDeranaScraper()
  └─ 2. Fallback: ConfigurableScraper.from_source_name(source_name)
              └─ Reads SourceConfig from PostgreSQL
```

---

### 1.3 Smart Cache Layer (scraper_tools.py)

The scraper tools add an important caching layer **on top of** the ConfigurableScraper:

```
_scrape_source_async(source_name, force_refresh)
  │
  ├─ SmartCacheManager.should_scrape(source_name, url, source_type)
  │     ├─ ETag header check  ← HTTP conditional GET
  │     ├─ Last-Modified check
  │     └─ Content signature hash comparison
  │
  ├─ CACHE HIT → return cache.get_cached_articles(source_name)
  │               [Zero scraping cost, ~70% hit rate claimed]
  │
  └─ CACHE MISS → scraper.fetch_articles()
                   └─ cache.cache_articles(source_name, url, articles)
                   └─ update_scrape_result(source_name, count, success=True)
```

**Cache check methods by source type:**

| Source Type | Detection Strategy |
|---|---|
| `"news"` | RSS feed check → ETag → Content signature |
| `"api"` | ETag header only |
| `"static"` | Last-Modified header |

---

### 1.4 Parallel Scraping

`scraper_tools.py` **does have** `scrape_multiple_sources()` using `asyncio.gather()`:
```python
tasks = [_scrape_source_async(name) for name in source_names]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

✅ **This works correctly.** The bug identified in the audit is specifically in `master_orchestrator.py`'s `_scrape_content_node` which uses a **for-loop instead of calling this function**.

---

### 1.5 Integration Pipeline (integration/pipeline.py)

This is a **separate, parallel orchestration path** from the LangGraph orchestrator. It handles the Layer 2 → Layer 3 → Layer 4 data transformation pipeline.

```
IntegrationPipeline.run_full_pipeline(company_profile)
  │
  ├─ Layer 2: validate_layer2_output()   ← National indicators
  │
  ├─ Layer 3: l2_to_l3_adapter.adapt()  ← Maps NI → Operational Indicators
  │     └─ _simulate_layer3() if no real L3 processor
  │
  └─ Layer 4: _run_layer4_builtin()      ← Risk + Opportunity + Recommendations
        ├─ RuleBasedRiskDetector.detect_risks()
        ├─ RuleBasedOpportunityDetector.detect_opportunities()
        ├─ RecommendationEngine.generate_recommendations()
        └─ groq_insight_service.generate_recommendations()  ← LLM enhancement
```

**Builder Pattern:** `PipelineBuilder` allows clean composition:
```python
pipeline = PipelineBuilder()
    .with_layer2(my_l2_processor)
    .with_layer3(my_l3_processor)
    .with_layer4(my_l4_processor)
    .build()
```

---

### 1.6 Issues Found in Scraping Framework

#### Critical
| # | Issue | Location | Impact |
|---|---|---|---|
| 🔴 1 | Session leak in `from_source_name()` | `configurable_scraper.py` | DB connection exhaustion |
| 🔴 2 | Rate limiter resets every cycle | `configurable_scraper.py:_request_times` | IP blocking risk |
| 🔴 3 | `scrape_source()` uses `asyncio.get_event_loop()` | `scraper_tools.py:271` | Deprecated in Python 3.10+, raises `DeprecationWarning` |

#### High
| # | Issue | Location | Impact |
|---|---|---|---|
| 🟠 4 | Article cap hardcoded at 20 | `configurable_scraper.py:158` | Can't tune per source |
| 🟠 5 | `AdaDeranaScraper` bypasses `ConfigurableScraper` | `scraper_tools.py:SCRAPER_REGISTRY` | Dual code path, no rate limiting |
| 🟠 6 | `check_breaking_signals()` is a stub | `scraper_tools.py:338` | `# TODO` — returns empty always |
| 🟠 7 | `SOURCE_CONFIG` only has 3 sources hardcoded | `scraper_tools.py:48` | New DB sources won't get smart cache checking |

#### Medium
| # | Issue | Location | Impact |
|---|---|---|---|
| 🟡 8 | `_simulate_layer3()` uses hardcoded thresholds (30, 80) | `integration/pipeline.py:308` | Not configurable |
| 🟡 9 | `_store_layer4_results()` open `SessionLocal()` without `try/finally` | `integration/pipeline.py:616` | Session leak |
| 🟡 10 | No retry logic anywhere in scraper chain | All scraper files | Lost articles on transient failures |

---

## Part 2 — Intelligent Deduplication System

### 2.1 File Inventory

| File | Size | Role |
|---|---|---|
| `app/deduplication/__init__.py` | 70 lines | Module entry point, global singleton factory |
| `app/deduplication/semantic_deduplicator.py` | 666 lines | Main orchestrator — 3-level detection |
| `app/deduplication/embedding_generator.py` | 366 lines | Sentence-BERT embedding generation with Redis cache |
| `app/deduplication/similarity_engine.py` | 512 lines | FAISS vector store + similarity search |
| `app/deduplication/duplicate_cluster.py` | 506 lines | Story cluster management and cross-source aggregation |

**Total: ~2,120 lines** — this is a full, self-contained subsystem.

---

### 2.2 Architecture — How Deduplication Works

```
Article (title, body, url, source_name)
         │
         ▼
SemanticDeduplicator.check_duplicate()
         │
  ┌──────┴────────────────────────────────────┐
  │        LEVEL 1: URL Hash Check            │  O(1) — fastest
  │  _url_hash(url) → Redis GET dedup:url:{h} │
  └──────┬───────────────────────┬────────────┘
         │ HIT                   │ MISS
         ▼                       ▼
    DuplicateResult          LEVEL 2: Content Hash Check         O(1)
    EXACT_URL                _content_hash(title, body[:500])
    reject                   → Redis GET dedup:content:{h}
                                       │ MISS
                                       ▼
                             LEVEL 3: Semantic Similarity        O(log n)
                             embedding_generator.generate(text)
                             └─ sentence-BERT / TF-IDF fallback
                             similarity_engine.search(embedding, top_k=10)
                             └─ FAISS IndexFlatIP / numpy fallback
                                       │
                        ┌─────────────┼─────────────────┐
                        │             │                  │
                     sim ≥ 0.85   0.70 ≤ sim < 0.85   sim < 0.70
                        │             │                  │
                  NEAR_DUPLICATE  RELATED_STORY        UNIQUE
                  reject/review    accept             accept
                                       │                  │
                                       └──── _register_article() ───┘
                                                 │
                                    Redis SETEX dedup:url:{h}  (7 days)
                                    Redis SETEX dedup:content:{h}  (7 days)
                                    similarity_engine.add_article(embedding)
```

---

### 2.3 Embedding Generation (embedding_generator.py)

**Models used:**

| Language | Model | Dimensions |
|---|---|---|
| English | `all-MiniLM-L6-v2` | 384 |
| Sinhala / Tamil | `paraphrase-multilingual-MiniLM-L12-v2` | 384 |
| Fallback | TF-IDF + TruncatedSVD | 384 |

**Caching flow:**
```
generate(text, language)
  │
  ├─ Redis GET embedding:{md5(text[:500])}
  │     └─ HIT → return np.array
  │
  └─ MISS → SentenceTransformer.encode(text)
               └─ Redis SETEX embedding:{hash} 24hr
               └─ return np.ndarray (normalized L2)
```

**Batch support:** `generate_batch()` checks cache per text, then batches uncached texts in a single `model.encode()` call with `batch_size=32`.

---

### 2.4 Similarity Engine (similarity_engine.py)

**FAISS index types:**

| Mode | Index Type | When to Use | Speed |
|---|---|---|---|
| Default | `IndexFlatIP` (exact) | < 100k articles | Exact but O(n) |
| Scale mode | `IndexIVFFlat` (approximate) | > 100k articles | ~10x faster, ~1% less accurate |

**Rolling window management:**
- Default: 48-hour window, max 50,000 articles
- Old articles removed when: (a) outside window OR (b) over max count
- FAISS index **rebuilt from scratch** when > 100 articles removed — expensive

**Persistence:** FAISS index state is saved to Redis:
```
dedup:index:article_ids   → JSON list of article IDs
dedup:index:metadata      → JSON dict of ArticleVector metadata
```
On startup, index is **reconstructed** from Redis embeddings.

---

### 2.5 Duplicate Cluster Manager (duplicate_cluster.py)

Manages story clusters — groups of articles reporting the same event from different sources.

**Cluster lifecycle:**
```
1. First near-duplicate detected
   └─ create_cluster(primary_article_id, title, source)
   
2. More near-duplicates found
   └─ add_to_cluster(cluster_id, article_id, similarity_score)
   
3. Primary article re-evaluated on each addition
   └─ _update_primary_selection()
       Score = credibility(40%) + word_count(30%) + recency(30%)
       
4. Two clusters can be merged
   └─ merge_clusters(id1, id2) → keeps older cluster, re-evaluates primary
   
5. Persisted to Redis: dedup:cluster:{cluster_id}
```

**Source credibility table (hardcoded):**
```python
{
    "government_gazette": 0.95,
    "central_bank":       0.95,
    "ada_derana":         0.90,
    "daily_mirror":       0.85,
    "hiru_news":          0.80,
    "newsfirst":          0.80,
    "default":            0.70
}
```

---

### 2.6 Integration Point

The deduplication system is **NOT yet connected to the main pipeline**. Here's the current gap:

```
master_orchestrator.py
  └─ _scrape_content_node()   ← produces List[RawArticle]
       │
       ▼
  _process_articles_node()    ← receives articles
  
  ⚠️ NO DEDUP CALL between scrape and process
```

The deduplication module exists as a standalone subsystem but `SemanticDeduplicator.check_duplicate()` is never called from the orchestrator. It would need to be wired in between scraping and processing:

```python
# What should happen (not yet implemented):
dedup = await get_deduplicator()
unique_articles = []
for article in scraped_articles:
    result = await dedup.check_duplicate(
        article_id=article.article_id,
        title=article.raw_content.title,
        body=article.raw_content.body,
        url=str(article.source.url),
        source_name=article.source.source_name,
        language=article.raw_content.language or "en"
    )
    if result.recommendation == "accept":
        unique_articles.append(article)
```

---

### 2.7 Issues Found in Deduplication System

#### Critical
| # | Issue | Location | Impact |
|---|---|---|---|
| 🔴 1 | **Deduplication is never called from orchestrator** | `master_orchestrator.py` | The entire dedup system is dead code in production flow |

#### High
| # | Issue | Location | Impact |
|---|---|---|---|
| 🟠 2 | FAISS index is **in-memory only** between restarts | `similarity_engine.py` | Redis saves metadata but rebuild on restart is O(n) and slow |
| 🟠 3 | `_save_to_redis()` only triggered every 100 additions | `similarity_engine.py:284` | Up to 99 articles lost if process crashes |
| 🟠 4 | `_cleanup_old_articles()` uses `list.remove()` in a loop | `similarity_engine.py:313` | O(n²) — slow for large windows |
| 🟠 5 | FAISS index rebuild on cleanup > 100 articles | `similarity_engine.py:316` | Full rebuild is O(n) — blocks the event loop |

#### Medium
| # | Issue | Location | Impact |
|---|---|---|---|
| 🟡 6 | Source credibility table is hardcoded in Python | `duplicate_cluster.py:136` | Can't add/adjust without code change |
| 🟡 7 | `_register_article()` silently swallows all Redis errors with bare `except: pass` | `semantic_deduplicator.py:330` | Registration failure is invisible |
| 🟡 8 | `DuplicateType.NEAR_DUPLICATE` used for **both** ≥ 0.95 AND ≥ 0.85 | `semantic_deduplicator.py:449-453` | Logic bug — should be `EXACT_CONTENT` for ≥ 0.95 |
| 🟡 9 | `_load_from_redis()` loads ALL embeddings at startup | `similarity_engine.py:156` | Memory spike on startup if index is large |
| 🟡 10 | `check_duplicate_sync()` only uses content hash, no FAISS | `semantic_deduplicator.py:551` | Sync path is significantly less accurate than async path |

#### Low
| # | Issue | Location | Impact |
|---|---|---|---|
| 🟢 11 | `get_deduplicator()` global singleton not thread-safe | `__init__.py:40` | Race condition in multi-worker startup |
| 🟢 12 | `_normalize_url()` uses `re.sub` inside function | `semantic_deduplicator.py:193` | Should compile regex at module level |
| 🟢 13 | `merge_clusters()` doesn't update Redis article-cluster mappings for merged members | `duplicate_cluster.py:402` | Stale mappings after merge |

---

## Part 3 — Combined System Map

### How These Systems Relate

```
┌─────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                      │
│                                                         │
│  SCRAPER_REGISTRY + DB (SourceConfig)                   │
│         │                                               │
│         ▼                                               │
│  ScraperToolManager.execute_scraper()                   │
│         │                                               │
│  SmartCacheManager                                      │
│  (ETag / Last-Modified / Content-Signature)             │
│         │                                               │
│         ▼                                               │
│  ConfigurableScraper  ←── DB CSS Selectors              │
│  (or AdaDeranaScraper)                                  │
│         │                                               │
│         ▼                                               │
│  List[RawArticle]                                       │
└─────────────────────┬───────────────────────────────────┘
                      │
           ⚠️ GAP: No dedup call here
                      │
┌─────────────────────▼───────────────────────────────────┐
│                DEDUPLICATION LAYER (disconnected)       │
│                                                         │
│  SemanticDeduplicator.check_duplicate()                 │
│         ├─ Level 1: URL Hash  → Redis O(1)              │
│         ├─ Level 2: Content Hash → Redis O(1)           │
│         └─ Level 3: FAISS Semantic → O(log n)           │
│                                                         │
│  DuplicateClusterManager                                │
│  (Story grouping + primary article selection)           │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                PROCESSING LAYER                         │
│                                                         │
│  ProcessingAgent → PriorityAgent → ValidationAgent      │
│         │                                               │
│         ▼                                               │
│  IntegrationPipeline (L2 → L3 → L4)                    │
│         ├─ Layer2ToLayer3Adapter                        │
│         ├─ RuleBasedRiskDetector                        │
│         ├─ RuleBasedOpportunityDetector                 │
│         └─ GroqInsightService (LLM)                     │
└─────────────────────────────────────────────────────────┘
```

---

## Part 4 — Top 10 Fixes (Prioritized)

| Priority | Fix | Files | Effort |
|---|---|---|---|
| 🔴 1 | **Wire `SemanticDeduplicator` into orchestrator** between scrape and process nodes | `master_orchestrator.py` | 2–3 hours |
| 🔴 2 | **Fix session leak** — add `with SessionLocal() as db:` in `from_source_name()` and `_store_layer4_results()` | `configurable_scraper.py`, `integration/pipeline.py` | 30 min |
| 🔴 3 | **Fix `asyncio.get_event_loop()` calls** in `scraper_tools.py` — use `asyncio.run()` or restructure to proper async | `scraper_tools.py:271` | 1 hour |
| 🟠 4 | **Move rate limit state to Redis** — `ZADD dedup:rate:{source}` instead of `_request_times` list | `configurable_scraper.py` | 2 hours |
| 🟠 5 | **Wire `SmartCacheManager` to DB sources** — extend `SOURCE_CONFIG` dict to auto-populate from `SourceConfig` table | `scraper_tools.py:48` | 1 hour |
| 🟠 6 | **Fix FAISS cleanup** — replace `list.remove()` loop with set-based removal + index rebuild via `asyncio.create_task()` to avoid blocking | `similarity_engine.py:309` | 1 hour |
| 🟠 7 | **Fix `DuplicateType` logic bug** — separate ≥ 0.95 into `EXACT_CONTENT`, keep ≥ 0.85 as `NEAR_DUPLICATE` | `semantic_deduplicator.py:449` | 15 min |
| 🟡 8 | **Add `tenacity` retry** to `httpx.get()` calls | `configurable_scraper.py` | 1 hour |
| 🟡 9 | **Move source credibility table to DB** — add `credibility_score` field to `SourceConfig` | `duplicate_cluster.py:136`, `models/agent_models.py` | 2 hours |
| 🟡 10 | **Make article cap DB-configurable** — add `max_articles_per_run` to `SourceConfig` | `configurable_scraper.py:158`, `models/agent_models.py` | 1 hour |

---

## Part 5 — Recommended Folder Structure for These Two Systems

Based on the analysis, here is where these files should live in the proposed reorganized structure:

```
backend/app/
│
├── ingestion/                      ← Rename from scrapers/
│   ├── scrapers/
│   │   ├── base.py                 ← Unchanged
│   │   ├── configurable.py         ← Rename from configurable_scraper.py
│   │   └── parsers/                ← Split from configurable_scraper.py
│   │       ├── link_extractor.py   ← _extract_article_links()
│   │       ├── content_parser.py   ← _extract_text(), _extract_body()
│   │       ├── date_parser.py      ← _parse_date()
│   │       └── image_extractor.py  ← _extract_images()
│   ├── cache/
│   │   └── smart_cache.py          ← SmartCacheManager (from app/cache/)
│   └── tools/
│       └── scraper_tools.py        ← Move from agents/tools/
│
├── deduplication/                  ← KEEP as-is, structure is clean
│   ├── __init__.py                 ← Global singleton factory
│   ├── semantic_deduplicator.py    ← Main engine
│   ├── embedding_generator.py      ← BERT embeddings
│   ├── similarity_engine.py        ← FAISS search
│   └── duplicate_cluster.py        ← Story clustering
│
├── pipeline/                       ← Rename from integration/
│   ├── orchestrator.py             ← Rename from pipeline.py
│   ├── adapters.py                 ← Layer-to-layer adapters
│   └── contracts.py                ← Pydantic inter-layer contracts
```

**What changes:** `ingestion/` subfolder splits `configurable_scraper.py` into focused parser modules. `deduplication/` stays as-is (already well-organized). `integration/` gets renamed to `pipeline/` for clarity.

---

## Summary Table

| System | Files | Lines | Status | Connected to Pipeline? |
|---|---|---|---|---|
| Universal Scraper | `base.py`, `configurable_scraper.py`, `ada_derana.py` | ~827 | ✅ Working | ✅ Yes (via `scraper_tools.py`) |
| Smart Cache Layer | `scraper_tools.py` (cache section) | ~532 | ✅ Working | ✅ Yes |
| Integration Pipeline | `pipeline.py`, `adapters.py`, `contracts.py` | ~1,500 | ✅ Working | ⚠️ Parallel path to LangGraph |
| Semantic Deduplication | All 5 files in `deduplication/` | ~2,120 | ✅ Complete code | ❌ **Never called** |
| Duplicate Clustering | `duplicate_cluster.py` | 506 | ✅ Complete code | ❌ **Only called by deduplicator** |

**Key takeaway:** The deduplication subsystem is the most sophisticated part of the codebase — 5 files, 2,120 lines, multi-level detection with FAISS + Redis — but it is **completely disconnected from the live pipeline**. Wiring it in is a 2-3 hour task that would immediately eliminate article duplication across runs.
