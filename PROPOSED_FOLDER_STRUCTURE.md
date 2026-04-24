# 📁 Proposed Folder Structure — National Activity Indicator
> **Philosophy:** Layer-discipline naming for the backend pipeline + domain naming elsewhere.  
> **Layer 1 = full Source Intelligence system** (scraping + agents + orchestration).  
> **Scalable:** Each layer can grow independently or be extracted into a microservice.

---

## Problems with Current Structure (Quick Reference)

| Problem | Example |
|---|---|
| `layer2`, `layer3`, `layer4`, `layer5` — cryptic names | No subtitle = tribal knowledge required |
| `layer2` has both `nlp/` and `nlp_processing/` | Duplicate concepts |
| `layer4` has 18 subdirectories, flat | Navigation nightmare |
| 105 files in `scripts/` — all mixed | Tests next to setup next to debug tools |
| 23 `.md` files flat in `backend/files/` | No grouping by topic |
| Docs scattered: root + `backend/files/` + `backend/docs/` | No single source of truth |
| `_archive` folders hidden inside source dirs | Indexed by linters and test runners |
| `deduplication/` exists but never wired to pipeline | Disconnected subsystem |
| `scraper_tools.py` lives in `agents/tools/` | Belongs to ingestion, not agents |
| `integration/` name unclear | Should be `pipeline/` |
| `reputation_manager.py` was a 600-line God Object | Modularized it to `reputation/` package |
| `quality_filter.py` mixes pre/post logic | Breaking it down into `filters/` module |

---

## Proposed Structure

```
NationalActivityIndicator_MAIN/
│
├── 📁 backend/                                  ← Python / FastAPI backend
│   │
│   ├── 📁 app/                                  ← Application source root
│   │   │
│   │   ├── 📁 core/                             ← Cross-cutting infrastructure (no layer owns)
│   │   │   ├── config.py                        ← Pydantic-settings app config
│   │   │   ├── logging.py                       ← structlog setup (activate this!)
│   │   │   ├── exceptions.py                    ← Custom exception classes
│   │   │   ├── security.py                      ← Auth / JWT helpers
│   │   │   │
│   │   │   └── 📁 llm/                          ← ★ Shared LLM Gateway (all layers use this)
│   │   │       ├── gateway.py                   ← LLMGateway: priority queue + connection pool
│   │   │       ├── manager.py                   ← Provider registry + fallback chain
│   │   │       ├── rate_limiter.py              ← Redis sliding-window rate limiter (shared)
│   │   │       ├── circuit_breaker.py           ← Per-provider failure state machine
│   │   │       └── config.py                    ← Provider limits, timeouts, model names
│   │   │
│   │   ├── 📁 db/                               ← Database infrastructure
│   │   │   ├── session.py                       ← SQLAlchemy engine + session factory
│   │   │   ├── base_class.py                    ← Declarative base
│   │   │   ├── 📁 postgres/
│   │   │   │   └── connection_pool.py           ← Pool manager, lifecycle hooks
│   │   │   ├── 📁 mongodb/
│   │   │   │   ├── client.py
│   │   │   │   └── entity_store.py
│   │   │   └── 📁 redis/
│   │   │       ├── client.py
│   │   │       └── cache_manager.py
│   │   │
│   │   ├── 📁 models/                           ← SQLAlchemy ORM models (DB schema)
│   │   │   ├── source.py                        ← SourceConfig, ScrapingSchedule
│   │   │   ├── article.py                       ← RawArticle, ProcessedArticle
│   │   │   ├── indicator.py                     ← Indicator, IndicatorValue
│   │   │   ├── agent.py                         ← AgentDecision, AgentMetrics
│   │   │   └── user.py
│   │   │
│   │   ├── 📁 schemas/                          ← Pydantic request/response schemas
│   │   │   ├── article.py
│   │   │   ├── indicator.py
│   │   │   ├── source.py
│   │   │   └── user.py
│   │   │
│   │   ├── 📁 api/                              ← FastAPI routers and endpoints
│   │   │   ├── deps.py                          ← Shared dependencies (get_db, etc.)
│   │   │   └── 📁 v1/
│   │   │       ├── router.py                    ← Master API router
│   │   │       ├── 📁 scraping/                 ← Scraping management endpoints
│   │   │       ├── 📁 indicators/               ← Indicator CRUD + history
│   │   │       ├── 📁 agents/                   ← Agent status + triggers
│   │   │       ├── 📁 dashboard/                ← Dashboard data endpoints
│   │   │       └── 📁 auth/                     ← Login, token endpoints
│   │   │
│   │   │   ════════════════════════════════════════════════════
│   │   │                  PIPELINE LAYERS
│   │   │   ════════════════════════════════════════════════════
│   │   │
│   │   ├── 📁 layer1/                           ← LAYER 1: Data Scraping & Source Intelligence
│   │   │   │          (Scraping, deduplication, ALL pipeline agents, orchestration)
│   │   │   │
│   │   │   ├── 📁 scrapers/                     ← Scraper engines
│   │   │   │   ├── base.py                      ← BaseScraper abstract class
│   │   │   │   ├── configurable.py              ← ConfigurableScraper (DB-driven)
│   │   │   │   └── 📁 parsers/                  ← Split from configurable_scraper.py
│   │   │   │       ├── link_extractor.py        ← _extract_article_links()
│   │   │   │       ├── content_parser.py        ← _extract_text(), _extract_body()
│   │   │   │       ├── date_parser.py           ← _parse_date()
│   │   │   │       └── image_extractor.py       ← _extract_images()
│   │   │   │
│   │   │   ├── 📁 sources/                      ← Site-specific scrapers
│   │   │   │   └── ada_derana.py                ← Migrate to ConfigurableScraper!
│   │   │   │
│   │   │   ├── 📁 deduplication/                ← ★ Semantic Deduplication Engine
│   │   │   │   ├── __init__.py                  ← Global singleton factory
│   │   │   │   ├── semantic_deduplicator.py     ← 3-level detection: URL→Hash→FAISS
│   │   │   │   ├── embedding_generator.py       ← Sentence-BERT + Redis cache
│   │   │   │   ├── similarity_engine.py         ← FAISS vector store + search
│   │   │   │   └── duplicate_cluster.py         ← Story clustering + cross-source
│   │   │   │
│   │   │   ├── 📁 cache/                        ← ★ Smart Scraping Cache (3 files, ~57KB)
│   │   │   │   ├── __init__.py                  ← Exports get_smart_cache, SmartCacheManager
│   │   │   │   ├── smart_cache.py               ← Cache manager: ETag / Last-Modified / Signature
│   │   │   │   ├── change_detector.py           ← Per-source change detection (RSS/HTML/API strategies)
│   │   │   │   └── cache_metrics.py             ← Hit rate, bandwidth saved, time saved per source
│   │   │   │
│   │   │   ├── 📁 reputation/                   ← ★ Source Reputation System [MODULARIZED]
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py                    ← Configuration & Data contracts
│   │   │   │   ├── repository.py                ← Data Access DB Ops
│   │   │   │   ├── calculator.py                ← Math Engine (EMA, Decays)
│   │   │   │   ├── tasks.py                     ← CRON Tasks
│   │   │   │   └── manager.py                   ← System Facade
│   │   │   │
│   │   │   ├── 📁 filters/                      ← ★ Quality Pipeline Filters [NEWLY SPLIT]
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py                    ← Filter Configs & Results
│   │   │   │   ├── pre_filter.py                ← Validation against blacklist before NLP
│   │   │   │   ├── post_filter.py               ← ML vs Target Threshold scoring engine
│   │   │   │   └── manager.py                   ← QualityFilter API Facade
│   │   │   │
│   │   │   ├── 📁 feeds/                        ← RSS / Atom feed scrapers
│   │   │   │   └── rss_scraper.py
│   │   │   │
│   │   │   ├── 📁 apis/                         ← Third-party API clients
│   │   │   │   ├── central_bank.py
│   │   │   │   └── weather_api.py
│   │   │   │
│   │   │   ├── 📁 processing/                    ← ★ Pre-NLP text preparation [NEW — build this]
│   │   │   │   ├── language_detector.py          ← Detect article language: en / si / ta
│   │   │   │   └── translator.py                 ← Translate si/ta → en before Layer 2 NLP
│   │   │   │
│   │   │   ├── 📁 cross_validation/              ← ★ Cross-source fact corroboration (6 files, ~100KB)
│   │   │   │   ├── __init__.py                   ← Module entry point
│   │   │   │   ├── validation_network.py         ← Multi-source validation graph
│   │   │   │   ├── claim_extractor.py            ← Extract verifiable claims from articles
│   │   │   │   ├── corroboration_engine.py       ← Match claims across sources
│   │   │   │   ├── source_reputation.py          ← Source credibility + reputation scoring
│   │   │   │   └── trust_calculator.py           ← Final trust score aggregation
│   │   │   │
│   │   │   ├── 📁 agents/                       ← ★ All pipeline agents
│   │   │   │   ├── base_agent.py                ← Abstract agent base (uses core/llm/gateway)
│   │   │   │   ├── config.py                    ← Agent scheduling + behaviour config
│   │   │   │   ├── source_monitor_agent.py      ← Monitors which sources need scraping
│   │   │   │   ├── scheduler_agent.py           ← Adaptive frequency optimization
│   │   │   │   ├── processing_agent.py          ← Article cleaning + entity extraction
│   │   │   │   ├── priority_agent.py            ← Importance classification
│   │   │   │   ├── validation_agent.py          ← Quality scoring + threshold checks
│   │   │   │   └── 📁 tools/                   ← LangChain tool wrappers
│   │   │   │       ├── scraper_tools.py         ← ScraperToolManager + smart cache
│   │   │   │       ├── database_tools.py        ← DB read/write tools
│   │   │   │       └── processor_tools.py       ← Processing helper tools
│   │   │   │
│   │   │   └── 📁 orchestrator/                 ← Layer 1 pipeline coordination
│   │   │       ├── master.py                    ← LangGraph master orchestrator
│   │   │       ├── state.py                     ← OrchestratorState + state manager
│   │   │       └── 📁 pipeline/                 ← Inter-layer data contracts
│   │   │           ├── integration.py           ← IntegrationPipeline (L2→L3→L4)
│   │   │           ├── adapters.py              ← Layer-to-layer data adapters
│   │   │           └── contracts.py             ← Pydantic inter-layer contracts
│   │   │
│   │   ├── 📁 layer2/                           ← LAYER 2: NLP Processing & Classification
│   │   │   │          (Text cleaning, NER, ML classification, indicator extraction)
│   │   │   │          [Current: app/layer2/ — rename subfolders only]
│   │   │   │
│   │   │   ├── 📁 cleaning/                     ← Text normalization, dedup
│   │   │   ├── 📁 nlp/                          ← NER, spaCy (merge nlp + nlp_processing)
│   │   │   ├── 📁 classification/               ← ML classifiers
│   │   │   ├── 📁 indicators/                   ← Indicator extraction from text
│   │   │   ├── 📁 data_ingestion/               ← Keep as-is
│   │   │   ├── 📁 storage/                      ← Keep as-is
│   │   │   └── pipeline.py                      ← Layer 2 pipeline entry point
│   │   │
│   │   ├── 📁 layer3/                           ← LAYER 3: Operational Analysis
│   │   │   │          (Indicator scoring, trend analysis, forecasting)
│   │   │   │          [Current: app/layer3/ — restructure internals]
│   │   │   │
│   │   │   ├── 📁 engine/                       ← Scoring + analysis logic
│   │   │   ├── 📁 trends/                       ← Trend + forecast calculation
│   │   │   ├── 📁 data/                         ← Data files
│   │   │   ├── 📁 storage/                      ← Keep as-is
│   │   │   └── pipeline.py
│   │   │
│   │   ├── 📁 layer4/                           ← LAYER 4: LLM Intelligence Engine
│   │   │   │          (Risk, opportunity, recommendation, narrative generation)
│   │   │   │          [Current: app/layer4/ — reorganize 18 subdirs]
│   │   │   │          [LLM calls go via core/llm/gateway.py — no direct API calls here]
│   │   │   │
│   │   │   ├── 📁 llm/                          ← Layer 4 LLM usage (prompts + response parsing)
│   │   │   │   ├── groq_insight_service.py      ← Narrative + insight generation (calls gateway)
│   │   │   │   └── prompt_templates.py          ← Layer 4 prompt templates
│   │   │   ├── 📁 risk/                         ← Risk detection engine
│   │   │   ├── 📁 opportunity/                  ← Opportunity detection
│   │   │   ├── 📁 recommendation/               ← Recommendation engine
│   │   │   ├── 📁 narrative/                    ← Report/narrative generation
│   │   │   ├── 📁 scoring/                      ← Scoring + prioritization
│   │   │   ├── 📁 cache/                        ← Layer 4 result caching
│   │   │   ├── 📁 storage/                      ← Insight persistence
│   │   │   └── pipeline.py
│   │   │
│   │   ├── 📁 layer5/                           ← LAYER 5: Dashboard & User API
│   │   │   │          (Company context, feedback, personalization)
│   │   │   │          [Current: app/layer5/ — keep structure]
│   │   │   │
│   │   │   ├── 📁 api/                          ← Layer 5 specific endpoints
│   │   │   ├── 📁 models/                       ← Layer 5 specific models
│   │   │   ├── 📁 schemas/                      ← Layer 5 specific schemas
│   │   │   ├── 📁 services/                     ← Layer 5 services
│   │   │   └── config.py
│   │   │
│   │   └── main.py                              ← FastAPI app factory + lifespan
│   │
│   ├── 📁 tests/                                ← All tests (move from scripts/)
│   │   ├── 📁 unit/
│   │   │   ├── test_scrapers.py
│   │   │   ├── test_deduplication.py             ← ★ Add these!
│   │   │   ├── test_parsers.py
│   │   │   └── test_agents.py
│   │   ├── 📁 integration/
│   │   │   ├── test_pipeline.py
│   │   │   ├── test_db_connections.py
│   │   │   └── test_api_endpoints.py
│   │   └── conftest.py                          ← pytest fixtures
│   │
│   ├── 📁 scripts/                              ← Operational scripts (organized)
│   │   ├── 📁 setup/                            ← One-time setup
│   │   │   ├── init_databases.py
│   │   │   ├── populate_sources.py              ← populate_source_configs.py
│   │   │   └── create_admin.py
│   │   ├── 📁 data/                             ← Data generation + seeding
│   │   │   ├── generate_mock_data.py
│   │   │   └── generate_historical.py
│   │   └── 📁 ops/                              ← Operational / debug scripts
│   │       ├── run_scraper.py
│   │       ├── run_pipeline.py
│   │       └── check_health.py
│   │
│   ├── 📁 data/                                 ← Runtime data (not source code)
│   │   ├── 📁 training/                         ← ML training datasets
│   │   └── 📁 exports/                          ← Data exports
│   │
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── alembic.ini
│   └── Dockerfile
│
├── 📁 frontend/                                 ← Next.js frontend (rename from src/)
│   ├── 📁 app/                                  ← Next.js App Router pages
│   ├── 📁 components/
│   │   ├── 📁 charts/
│   │   ├── 📁 indicators/
│   │   ├── 📁 maps/
│   │   ├── 📁 widgets/
│   │   └── 📁 shared/                           ← Reusable UI primitives
│   ├── 📁 hooks/
│   ├── 📁 lib/
│   ├── 📁 types/
│   └── 📁 styles/
│
├── 📁 infra/                                    ← Infrastructure configuration
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── 📁 nginx/
│   │   └── nginx.conf
│   └── 📁 scripts/                              ← Shell / PowerShell ops
│       ├── run-continuous-scraping.ps1
│       └── run-migrations.sh
│
├── 📁 docs/                                     ← ALL documentation (centralized)
│   ├── 📁 architecture/
│   │   ├── OVERVIEW.md                          ← System overview
│   │   ├── PIPELINE_LAYERS.md                   ← What each layer does
│   │   ├── DATA_FLOW.md                         ← Data flow diagrams
│   │   └── PROPOSED_FOLDER_STRUCTURE.md         ← THIS FILE
│   ├── 📁 setup/
│   │   ├── QUICKSTART.md
│   │   ├── DOCKER_SETUP.md
│   │   └── WEATHER_API_SETUP.md
│   ├── 📁 api/
│   │   └── API_REFERENCE.md
│   ├── 📁 audits/                               ← Code audit reports
│   │   ├── SCRAPING_LAYER_AUDIT.md              ← ★ Generated audit
│   │   └── SCRAPING_AND_DEDUPLICATION_ANALYSIS.md ← ★ Generated analysis
│   ├── 📁 reports/                              ← Historical dev reports
│   │   ├── DAY2_COMPLETION_REPORT.md
│   │   ├── DAY3_FINAL_REPORT.md
│   │   └── ...all DAY*.md files...
│   └── 📁 guides/
│       ├── BERT_EMBEDDINGS_GUIDE.md
│       ├── SCALING_STRATEGY.md
│       └── PRODUCTION_SCALABILITY_GUIDE.md
│
├── 📁 _archive/                                 ← Dead code (outside src tree)
│   ├── 📁 old_scrapers/                         ← Retired scrapers
│   └── 📁 old_pages/                            ← From _archive_old_pages/
│
├── .gitignore
├── .env.example                                 ← Template (no real secrets!)
└── README.md
```

---

## Migration Map — Where Things Move

### Layer 1 (biggest changes — consolidation of scattered modules)

| Current Path | New Path | Notes |
|---|---|---|
| `app/scrapers/base.py` | `app/layer1/scrapers/base.py` | Move |
| `app/scrapers/configurable_scraper.py` | `app/layer1/scrapers/configurable.py` | Move + rename |
| `app/scrapers/news/ada_derana.py` | `app/layer1/sources/ada_derana.py` | Move |
| `app/deduplication/` (all 5 files) | `app/layer1/deduplication/` | Move entire folder |
| `app/cache/` (all 4 files) | `app/layer1/cache/` | Move entire folder |
| `app/services/reputation/` | `app/layer1/reputation/` | Relocate newly modularized reputation system |
| `app/services/quality_filter.py` | `app/layer1/filters/` | Breakdown into pre_filter, post_filter components |
| `app/agents/base_agent.py` | `app/layer1/agents/base_agent.py` | Move into layer1 |
| ... (other agents and tools follow same pattern) |

## Quick Wins Update

```
...
7.  Create infra/ folder, move docker-compose.yml there
    Then (requires import path updates):
8.  Move new app/services/reputation/ → app/layer1/reputation/
9.  Move new app/services/filters/ → app/layer1/filters/
10. Move app/scrapers/ → app/layer1/scrapers/
...
```
