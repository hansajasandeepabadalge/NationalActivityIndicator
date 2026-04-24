# 🔍 Scraping & Source Intelligence Layer — Production Audit

> **Project:** National Activity Indicator  
> **Audit Scope:** Data Scraping, Parsing, Configuration, Networking, Scheduling  
> **Date:** 2026-04-07

---

## 1. Codebase Mapping

### Module Groupings

| Module | Files | Responsibility |
|---|---|---|
| **Scraper Core** | `scrapers/configurable_scraper.py`, `scrapers/base.py` | Universal HTML scraping engine |
| **Site-Specific Scrapers** | `scrapers/news/ada_derana.py` | Hardcoded per-site scraper |
| **Config / Settings** | `core/config.py`, `agents/config.py`, `core/llm_config.py` | App settings, LLM settings |
| **Data Models** | `models/raw_article.py`, `models/agent_models.py` (SourceConfig) | Pydantic & SQLAlchemy models |
| **Networking / DB** | `db/session.py`, `db/connection_pool.py`, `db/mongodb.py`, `db/redis_manager.py` | DB connections, pooling |
| **Scheduling** | `agents/scheduler_agent.py`, `models/agent_models.py` (ScrapingSchedule) | Adaptive scraping scheduling |
| **Orchestration** | `orchestrator/master_orchestrator.py`, `orchestrator/state_manager.py` | LangGraph pipeline coordinator |
| **Agents** | `agents/source_monitor_agent.py`, `agents/processing_agent.py`, `agents/priority_agent.py`, `agents/validation_agent.py`, `agents/llm_manager.py` | AI processing, LLM routing |
| **Services** | `services/quality_filter.py`, `services/reputation_manager.py` | Post-scrape quality checks |
| **Scripts** | `scripts/populate_source_configs.py`, `scripts/run_scraper.py`, etc. | Setup, testing, one-off ops |

---

## 2. File-Level Analysis

### `scrapers/base.py` (74 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Abstract base class defining the scraper contract |
| **Inputs** | `source_id: int`, `source_name: str`, `base_url: str` |
| **Outputs** | `RawArticle` Pydantic objects via `create_article()` |
| **Core Logic** | Defines `fetch_articles()` as abstract; provides `create_article()` factory and `run()` with logging |
| **Patterns** | Template Method, Abstract Factory |
| **Dependencies** | `models/raw_article.py` (internal), Python `abc` |
| **Issues** | `create_article()` uses mutable default args (`images=[]`, `metadata={}`) — Python gotcha, shared state bug |
| | `job_id=0` hardcoded as placeholder — never resolved |
| | `scraper_version="1.0.0"` hardcoded |

---

### `scrapers/configurable_scraper.py` (624 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Universal DB-driven scraper; reads CSS selectors from `SourceConfig.selectors` JSONB |
| **Inputs** | `SourceConfig` ORM object from PostgreSQL; HTTP responses |
| **Outputs** | `List[RawArticle]` Pydantic models |
| **Core Logic** | (1) Rate-limit-wait → (2) Fetch list page → (3) Extract article links → (4) For each link: rate-limit-wait → fetch → parse → emit `RawArticle` |
| **Algorithms** | Sliding-window rate limiter, 3-fallback link extraction, multi-format date parser, lazy-loading image support |
| **Dependencies** | `httpx`, `BeautifulSoup4`/`lxml`, `re`, `asyncio`, `SourceConfig`, `RawArticle` |

#### Key Issues:
- **Hard article cap of 20 per run** (`article_links[:20]`) — not configurable per source
- **No deduplication** before returning — same article can be scraped multiple times on consecutive runs
- **`from_source_name()` is synchronous** — opens/closes a raw `SessionLocal()` session in a classmethod, not using the DI pattern the rest of the app uses
- **Session leak risk** — if `db.query()` raises after `db = SessionLocal()`, `db.close()` is never called (no `try/finally`)
- **Rate limiter is instance-scoped** — `_request_times` is per-scraper-instance; if the scraper is re-instantiated per run, rate limiting resets on every cycle — it provides zero cross-run protection
- **`_parse_date()`** uses `__import__('datetime')` inside lambdas — anti-pattern, fragile, should be a top-level import
- **`_extract_body()` clones BeautifulSoup elements with `.__copy__()`** — `BeautifulSoup` objects are not standard Python objects; this is unreliable and may silently fail
- **Bare except clause** at line 351 (`except: pass`) — swallows all exceptions silently
- **`body_exclude` selector uses one `exclude_selector` string for all body fallbacks** — logic bug, `exclude_selector` applies to all iterations indiscriminately

---

### `scrapers/news/ada_derana.py` (129 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Hardcoded scraper for Ada Derana (Sri Lankan news) |
| **Inputs** | Implicit `https://www.adaderana.lk/hot-news/` |
| **Outputs** | `List[RawArticle]` |
| **Core Logic** | Fetch list → find all links matching `/news/` → fetch each → extract title, body, date, images |
| **Issues** | `source_id=1` hardcoded — fragile assumption |
| | Date parsing is **commented out** (line 99: `pass`) — `publish_date` is always `None` |
| | No rate limiting whatsoever |
| | No article count limit — will scrape unlimited articles |
| | `base_url` uses `http://` (insecure) but `news_url` uses `https://` — inconsistency |
| | `_process_article()` does not check for empty body — will emit empty articles |
| | This scraper **bypasses** the `ConfigurableScraper` pattern — dead divergence |

---

### `models/agent_models.py` — `SourceConfig` (lines 226–325)
| Attribute | Details |
|---|---|
| **Purpose** | SQLAlchemy ORM model for per-source scraping configuration |
| **Key Fields** | `selectors` (JSONB), `rate_limit_requests`, `rate_limit_period`, `scraper_class`, `requires_javascript`, `is_active` |
| **`get_selectors()`** | Returns merged defaults + DB overrides |
| **Issues** | `requires_javascript = True` sources have no Playwright/Selenium implementation — the flag is stored but never acted upon |
| | `display_name` property falls back to `source_name.replace("_", " ").title()` — can produce ugly names |
| | `AgentMetrics` uses `class Meta: unique_together` (Django syntax) — **invalid for SQLAlchemy**; constraint is silently ignored |

---

### `models/raw_article.py` (40 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Pydantic v2 model for raw scraped content |
| **Issues** | `RawContent.url` is `Optional[str]` not `HttpUrl` — loses URL validation |
| | `SourceInfo.url` is `HttpUrl` but `RawContent.url` is `str` — inconsistent |
| | `images: List[Dict[str, str]] = []` — mutable default in Pydantic (v2 handles this, but it's a smell) |

---

### `core/config.py` (120 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Pydantic-settings based app configuration |
| **Issues** | `POSTGRES_PASSWORD = "postgres_secure_2024"` hardcoded as **default** in the class body — if the `.env` file is missing or misconfigured, production runs with a known password |
| | Same for `MONGO_PASSWORD`, `PGADMIN_PASSWORD` |
| | `DEBUG: bool = True` defaults to debug mode |
| | `USE_MOCK_DATA: bool = True` defaults to mock data — easy to forget to flip in production |
| | `get_database_url()` Docker detection heuristic uses `os.path.exists('/.dockerenv')` — unreliable in some container runtimes |

---

### `db/session.py` (88 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Creates sync + async SQLAlchemy engines and exposes `get_db()` / `get_async_session()` |
| **Issues** | `_get_async_database_url()` does a string replace only for `postgresql://` — the default URL format is `postgresql+psycopg://`, which would **not be converted** correctly to `postgresql+asyncpg://` |
| | Async engine creation wrapped in `try/except` that silently falls back to a stub that raises `NotImplementedError` — no startup warning |
| | Two separate engines/session factories (`session.py` + `connection_pool.py`) — dual initialization, no guaranteed consistency |

---

### `db/connection_pool.py` (320 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Enhanced pool manager with lifecycle hooks, health checks, statistics |
| **Issues** | `dispose()` calls `asyncio.get_event_loop().run_until_complete()` — deprecated pattern in Python 3.10+, will raise `DeprecationWarning` or fail |
| | `checked_out` counter in `on_checkout`/`on_checkin` events is not thread-safe (no lock) |
| | Pool manager is a global singleton but `session.py` also creates its own engine — two separate pool managers active simultaneously |

---

### `agents/scheduler_agent.py` (380 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Adaptive scrape frequency optimizer using rule-based logic + LLM prompt |
| **Inputs** | `scraping_schedule` table + source reliability metrics |
| **Outputs** | Frequency change recommendations; writes to `scraping_schedule` table |
| **Algorithms** | Article-yield heuristics, exponential backoff on failures, frequency clamping by priority class |
| **Issues** | `get_tools()` returns `[]` — despite inheriting `BaseAgent` which sets up LLM infrastructure, the scheduler does **not use the LLM** despite having `SCHEDULER_PROMPT` defined |
| | **`run_daily_optimization()` does a dry-run then immediately force-applies** — there is no gate/confirmation mechanism |
| | Frequency limits are hardcoded in `FREQUENCY_LIMITS` dict — not DB-configurable |

---

### `orchestrator/master_orchestrator.py` (712 lines)
| Attribute | Details |
|---|---|
| **Purpose** | LangGraph StateGraph that coordinates all agent phases |
| **Pipeline** | `monitor_sources → scrape_content → process_articles → classify_priority → validate_quality → store_articles` |
| **Issues** | **Line 560-562: `# TODO: Implement actual storage`** — storage node does **not** actually write to any DB. It marks articles as `"storage_status": "success"` but never persists them |
| | Scraping in `_scrape_content_node` is sequential (for-loop) despite the docstring saying "runs scrapers in parallel" |
| | `OrchestratorState` accumulates entire article lists in RAM — no streaming or pagination |

---

### `agents/base_agent.py` (237 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Abstract agent base with LLM access, timing, and `log_agent_decision()` |
| **Issues** | `llm_provider="groq"` hardcoded in both success and failure log calls — always logs as Groq even when a fallback was used |
| | `_create_agent_executor()` is defined but never called by any concrete agent — dead code |

---

### `agents/llm_manager.py` (313 lines)
| Attribute | Details |
|---|---|
| **Purpose** | Multi-provider LLM router: Groq → DeepSeek → Together.ai → OpenAI |
| **Rate Limit Check** | `_is_groq_rate_limited()` checks in-memory `groq_requests` counter — resets on every server restart | 
| **Issues** | Usage tracking is in-memory only — lost on restart, no persistence |
| | `_get_together_llm()` uses deprecated `langchain_community.llms.Together` class |
| | OpenAI model hardcoded as `"gpt-3.5-turbo"` regardless of `model_config.model_name` |

---

## 3. Architecture Flow

```
[SourceConfig DB] ──selectors──▶ ConfigurableScraper
                                        │
                          [rate_limit_wait]
                                        │
                              httpx.AsyncClient.get(list_url)
                                        │
                              BeautifulSoup.select(link_selector)
                               OR regex pattern match
                               OR heuristic fallback
                                        │
                         [per-article: rate_limit_wait + httpx.get]
                                        │
                              _extract_text / _extract_body
                              _extract_images / _parse_date
                                        │
                                  RawArticle (Pydantic)
                                        │
                        ┌───────────────▼──────────────────┐
                        │        MasterOrchestrator         │
                        │    (LangGraph StateGraph)         │
                        │                                   │
                        │  monitor_sources                  │
                        │       ↓                           │
                        │  scrape_content  ◀── scraper_mgr  │
                        │       ↓                           │
                        │  process_articles ◀── ProcessingAgent │
                        │       ↓                           │
                        │  classify_priority ◀── PriorityAgent  │
                        │       ↓                           │
                        │  validate_quality ◀── ValidationAgent │
                        │       ↓                           │
                        │  store_articles ← ⚠️ TODO stub    │
                        └───────────────────────────────────┘
                                        │
                              PostgreSQL (TimescaleDB)
                              MongoDB (entity/article store)
                              Redis (caching)
```

**Entry Points:**
- `scripts/run_scraper.py` — manual scraper invocation
- `run-continuous-scraping.ps1` — PowerShell polling loop
- `app/main.py` → API endpoint triggers (via FastAPI, agent orchestrator)
- `SchedulerAgent.run_daily_optimization()` — called automatically by orchestrator

---

## 4. Config System Analysis

### How CSS Selectors Are Stored

**Storage:** `source_configs.selectors` column — PostgreSQL JSONB

**Schema:**
```json
{
  "list_url": "https://example.com/news",
  "article_link_pattern": "/news/\\d+",
  "article_link_selector": "a.article-link",
  "title": "h1.article-title",
  "body": "div.article-content",
  "body_exclude": ".ad,.sidebar",
  "date": "span.pub-date",
  "date_format": "%B %d, %Y",
  "author": "span.author",
  "image": "div.content img",
  "pagination": "a.next"
}
```

**Retrieval:** `SourceConfig.get_selectors()` merges stored JSONB with hardcoded defaults.

### Flexibility Assessment

| Feature | Status |
|---|---|
| Per-source CSS selectors | ✅ DB-driven |
| Multi-selector fallback | ✅ Supports comma-separated + list |
| Date format per source | ✅ DB configurable |
| Rate limits per source | ✅ DB configurable |
| Scraper class selection | ✅ `scraper_class` field |
| Article cap (20) | ❌ Hardcoded |
| Retry count | ❌ Hardcoded (no retry at all) |
| Timeout | ❌ Hardcoded at 30s |
| JS rendering | ❌ Flag stored, never enforced |
| Pagination | ❌ Field defined, never used |

**Verdict:** Config is **partially dynamic**. Core selectors are DB-driven, but operational parameters (limits, timeouts, retries) are hardcoded in the Python source.

---

## 5. Rate Limiting & Performance

### Implementation

```python
# In ConfigurableScraper.__init__
self.rate_limit = source_config.rate_limit_requests or 10   # default 10
self.rate_period = source_config.rate_limit_period or 60    # default 60s

# In _rate_limit_wait()
self._request_times = [t for t in self._request_times if now - t < self.rate_period]
if len(self._request_times) >= self.rate_limit:
    wait_time = self.rate_period - (now - oldest)
    await asyncio.sleep(wait_time)
self._request_times.append(now)
```

### Assessment

| Criterion | Verdict |
|---|---|
| **Scope** | Per-scraper-instance (not per-domain, not global) |
| **Persistence** | In-memory only — resets on each scraper instantiation |
| **Cross-run protection** | ❌ None — if scraper is re-created per cycle, rate limit resets |
| **Concurrent scraper safety** | ❌ No shared state between parallel instances |
| **`AdaDeranaScraper` rate limiting** | ❌ Zero — no rate limiting at all |
| **Configurable** | ✅ Per-source from DB |
| **Algorithm** | Sliding window (correct approach) |
| **Risk** | Medium-High — potential IP blocking if multiple scrapers hit same domain, or run frequently in loops |

**Critical Gap:** The `run-continuous-scraping.ps1` script loops every N seconds and re-instantiates scrapers each cycle, defeating the in-memory rate limiter entirely.

---

## 6. Code Quality & Issues

### Dead Code
- `BaseAgent._create_agent_executor()` — defined but never called
- `SchedulerAgent.SCHEDULER_PROMPT` — prompt defined but `get_tools()` returns `[]` and LLM is not invoked
- `models/agent_models.py` → `class Meta: unique_together` inside `AgentMetrics` — Django-style, silently ignored in SQLAlchemy
- `pagination` field in `SourceConfig.selectors` — defined in docs/schema but never processed in `ConfigurableScraper`
- `RawContent.html` field — set to `None` always, never populated

### Tight Coupling
- `ConfigurableScraper.from_source_name()` directly instantiates `SessionLocal()` — bypasses all dependency injection, tightly couples scraper to DB
- `MasterOrchestrator.__init__` creates all agents eagerly — if any agent's dependency fails, the entire orchestrator fails to init
- `BaseAgent` hardcodes `llm_provider="groq"` in all log calls

### Hardcoded Values
- Article cap: `article_links[:20]` (line 158)
- HTTP timeout: `30.0` (lines 27, 144)
- Image limit: `[:5]` (line 446, 489)
- Body minimum length: `100` chars
- Paragraph minimum length: `20`/`50` chars
- Backoff formula: `2 ** (failures - 2)`
- DB passwords in class body defaults
- Scraper version: `"1.0.0"`
- `job_id=0` placeholder
- `quality_score=30.0`/`70.0` in reputation recording

### Missing Error Handling
- `ada_derana.py:_process_article()` — no try/except; any parse failure propagates up
- `configurable_scraper.py` line 351: bare `except: pass` — silently ignores all CSS selector exceptions
- `db/session.py` async engine creation — falls back to a stub; no startup warning/crash
- `connection_pool.py:dispose()` — `asyncio.get_event_loop()` can raise `RuntimeError` if no loop exists

### Poor Modularization
- `configurable_scraper.py` is 624 lines doing scraping + link extraction + parsing + date parsing + image extraction + article ID generation — should be split
- `master_orchestrator.py` is 712 lines with node logic embedded in methods — each node should be a separate module
- `scripts/` folder has 105 files, many ad-hoc one-offs mixed with essential setup scripts — no organization

---

## 7. Security & Reliability Risks

### Injection Risks
| Risk | Detail |
|---|---|
| **CSS selector injection** | `SourceConfig.selectors` values are passed directly to `soup.select(sel)` — if a malicious selector escapes the DB, it could cause unexpected behavior (low severity, no code exec risk) |
| **Regex injection** | `article_link_pattern` from DB is passed to `re.compile()` without validation — a malformed regex raises `re.error` but is caught; a ReDoS regex could hang the process |
| **URL construction** | `_make_absolute_url()` does not sanitize `href` values — a `javascript:` URI could slip through (low impact in scraping context) |

### API Misuse
| Risk | Detail |
|---|---|
| **Groq rate limit** | Counter is in-memory only; multi-worker uvicorn deployments would each have their own counter, multiplying actual API calls |
| **httpx no retry** | No retry logic on 429/503 responses — one transient failure = lost article |
| **No `robots.txt` compliance** | Scraper does not check or respect `robots.txt` |
| **User-Agent is hardcoded browser string** | Potentially deceptive; should at minimum include project identifier |

### Failure Handling Gaps
| Gap | Location |
|---|---|
| Storage node is a stub | `master_orchestrator.py:560` — articles are "stored" in memory only |
| No circuit breaker | If a source consistently fails, it keeps being attempted every cycle |
| No alerting on consecutive failures | `ScrapingSchedule.consecutive_failures` is tracked but alerts only in dry-run output |
| No timeout on individual article processing | An article stuck in LLM processing can block the whole pipeline |

---

## 8. Missing or Weak Areas

### Logging
- ✅ `logging.getLogger(__name__)` used consistently
- ❌ No structured logging (JSON format) for machine parsing
- ❌ No request/response logging for HTTP calls
- ❌ Log levels are inconsistent — some debug info at `INFO` level
- Note: `structlog` is in `requirements.txt` but not used anywhere in scraping layer

### Monitoring
- ❌ No metrics exported (Prometheus, etc.)
- ❌ `AgentMetrics` table exists but aggregation pipeline to populate it is missing
- ❌ No alerting hooks for scraping failures
- ❌ Pool stats are collected but not exposed via API

### Retry Mechanisms
- ❌ Zero retry logic in `ConfigurableScraper` or `AdaDeranaScraper`
- ❌ `tenacity` is in `requirements.txt` but not used in scraping layer
- ❌ No exponential backoff on HTTP errors
- ❌ `SchedulerAgent` does schedule backoff but only changes frequency — it does not trigger retries within a cycle

### Scalability
- ❌ Sequential scraping in orchestrator (for-loop)
- ❌ All article state held in RAM in `OrchestratorState`
- ❌ No queue-based architecture (Celery, RQ, etc.)
- ❌ Single-threaded rate limiter defeats parallelism benefits

---

## 9. Improvement Suggestions

### High Priority (Fix First)

1. **Complete the storage stub** — `master_orchestrator.py` line 560's TODO means no data is actually persisted. This is the most critical gap.

2. **Fix session leak in `from_source_name()`:**
   ```python
   # Current (leaks on exception):
   db = SessionLocal()
   config = db.query(...).first()
   db.close()
   
   # Fixed:
   with SessionLocal() as db:
       config = db.query(...).first()
   ```

3. **Persist rate limit state externally** — Use Redis (already in the stack) to store `_request_times` so it survives restarts and is shared across workers:
   ```python
   # Store last N request timestamps in Redis ZSET keyed by source_name
   redis.zadd(f"rate:{source_name}", {str(now): now})
   redis.zremrangebyscore(f"rate:{source_name}", 0, now - period)
   ```

4. **Add retry with backoff using `tenacity`** (already installed):
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
   async def fetch_with_retry(client, url):
       return await client.get(url)
   ```

5. **Fix mutable default arguments in `BaseScraper.create_article()`:**
   ```python
   def create_article(self, ..., images: List[dict] = None, metadata: dict = None):
       images = images or []
       metadata = metadata or {}
   ```

### Medium Priority

6. **Make article cap DB-configurable** — Add `max_articles_per_run` to `SourceConfig`

7. **Parallelize scraping in orchestrator** — Replace sequential for-loop with `asyncio.gather()`:
   ```python
   results = await asyncio.gather(*[
       self.scraper_manager.execute_scraper(name) 
       for name in state["sources_to_scrape"]
   ], return_exceptions=True)
   ```

8. **Implement deduplication** — Check article URL hash against Redis/DB before processing — `faiss-cpu` is already installed for semantic dedup

9. **Remove `AdaDeranaScraper`** or migrate it to use `ConfigurableScraper` with a seed config — eliminates the dual code path

10. **Fix `AgentMetrics` SQLAlchemy constraint:**
    ```python
    # Add proper UniqueConstraint in __table_args__
    __table_args__ = (UniqueConstraint('agent_name', 'date'),)
    ```

### Low Priority / Refactoring

11. **Split `configurable_scraper.py`** into: `link_extractor.py`, `content_parser.py`, `date_parser.py`, `image_extractor.py`

12. **Add `robots.txt` compliance** via `urllib.robotparser`

13. **Switch to structured logging** — activate `structlog` which is already a dependency

14. **Move hardcoded constants to config** — timeouts, body length thresholds, article cap, image cap

15. **Add Playwright support** for `requires_javascript=True` sources — currently a dead knob

---

## 10. Summary

### Key Strengths
| Strength | Detail |
|---|---|
| ✅ **Dynamic CSS Configuration** | DB-driven selectors genuinely eliminate per-site code — well-architected concept |
| ✅ **Multi-fallback Parsing** | CSS selector → pattern → heuristic fallback is resilient |
| ✅ **LLM Provider Abstraction** | Groq→DeepSeek→Together→OpenAI fallback chain is smart |
| ✅ **Agent Architecture** | LangGraph pipeline is maintainable and extensible |
| ✅ **Connection Pool Monitoring** | `ConnectionPoolManager` with lifecycle events is production-grade |
| ✅ **Adaptive Scheduling** | Rule-based frequency optimizer with exponential backoff logic is correct |

### Critical Weaknesses

| # | Issue | Severity |
|---|---|---|
| 🔴 1 | **Storage node is a TODO stub** — no data is actually persisted by the orchestrator | **CRITICAL** |
| 🔴 2 | **In-memory rate limiter resets on every scraper re-instantiation** — provides false security | **HIGH** |
| 🔴 3 | **No retry logic** — a single network hiccup drops articles permanently | **HIGH** |
| 🔴 4 | **Session leak** in `from_source_name()` | **HIGH** |
| 🟠 5 | **Sequential scraping** in orchestrator despite async architecture | **MEDIUM** |
| 🟠 6 | **`AdaDeranaScraper` has no rate limiting and broken date parsing** | **MEDIUM** |
| 🟠 7 | **Hardcoded credentials** as class-level defaults in `Settings` | **MEDIUM** |
| 🟡 8 | **Article cap, timeouts, thresholds are not configurable** | **LOW-MEDIUM** |
| 🟡 9 | **`requires_javascript` flag is stored but never enforced** | **LOW** |

### What to Fix First (Priority Order)

```
1. Implement storage (master_orchestrator.py line 560)
2. Fix session leak + add try/finally in from_source_name()
3. Move rate limit state to Redis
4. Add tenacity retry on HTTP calls
5. Parallelize scraping with asyncio.gather()
6. Fix mutable default args in BaseScraper
7. Merge AdaDeranaScraper into ConfigurableScraper
8. Add deduplication before processing
9. Make article cap / timeout DB-configurable
10. Wire up structlog for structured logging
```
