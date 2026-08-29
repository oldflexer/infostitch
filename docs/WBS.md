# Work Breakdown Structure (WBS)
## News Aggregator & Publisher System

### 1. Project Setup
- 1.1. Create repository and directory structure.
- 1.2. Setup virtual environment (Python 3.13).
- 1.3. Add dependencies (SQLAlchemy, Alembic, httpx, structlog, prometheus_client, streamlit, pytest, etc.).
- 1.4. Create `.env.example` and configuration loader.
- 1.5. Configure linting (flake8, black, mypy) and pre-commit hooks.

### 2. Database & Domain Models
- 2.1. Define SQLAlchemy models for all tables.
- 2.2. Create Alembic migration scripts.
- 2.3. Define domain entities and value objects (Article, Post, Source, Channel, Embedding, Template).
- 2.4. Implement repository interfaces (in domain layer).
- 2.5. Implement SQLAlchemy repositories (infrastructure layer).

### 3. Core Services (Application)
- 3.1. LLM Service abstraction + Gemini implementation.
- 3.2. Embedding Service (uses LLM service or direct HTTP).
- 3.3. Content Extractor Service (Jina AI + image extraction logic).
- 3.4. Publisher Service (interface with methods for each channel).
- 3.5. Cache Service (in-memory TTL).
- 3.6. Deduplication Service (URL + Jaccard + embedding similarity).

### 4. Pipeline Steps
- 4.1. Fetch RSS Step.
- 4.2. Deduplicate Step (stage 1).
- 4.3. Select Top Candidates Step (call LLM for ranking).
- 4.4. Extract Content Step.
- 4.5. Generate Post Step (template selection + LLM).
- 4.6. Compute Embedding Step.
- 4.7. Deduplicate Step (stage 2 – embedding check).
- 4.8. Publish Step (calls Publisher Service for each channel).
- 4.9. Pipeline Orchestrator (run steps in order, handle errors).

### 5. CLI & Scheduling
- 5.1. Implement CLI entry point (`run.py`) that loads config, initializes DI, runs pipeline.
- 5.2. Create cron script to invoke CLI every 3 hours.
- 5.3. Add manual trigger option.

### 6. Dashboard (Streamlit)
- 6.1. Authentication (login page with user DB).
- 6.2. Overview page (pipeline status, metrics, last runs).
- 6.3. Logs page (filter by level, time).
- 6.4. Settings page (edit RSS, channels, thresholds, LLM models).
- 6.5. Manual actions (clear old data, trigger pipeline).
- 6.6. Metrics visualization (prometheus integration).

### 7. Error Handling, Logging & Monitoring
- 7.1. Implement structured logging (structlog) with context.
- 7.2. Implement retry decorator for HTTP clients.
- 7.3. Implement notification service (send Telegram message on critical errors).
- 7.4. Add Prometheus metrics (pipeline duration, success/failure counts, API call counts).
- 7.5. Integrate metrics with dashboard.

### 8. Testing
- 8.1. Unit tests for domain models and value objects.
- 8.2. Unit tests for services (with mocks).
- 8.3. Integration tests for repositories (with test DB).
- 8.4. Integration tests for pipeline steps (with mocked API responses).
- 8.5. E2E test (full run with test configuration, mocks for external APIs).
- 8.6. Test coverage report and quality gates.

### 9. Documentation
- 9.1. Write SRS, HLD, AD, WBS (this document), ROADMAP, TEST PLAN, QA EVAL.
- 9.2. Write code docstrings and README.
- 9.3. Create deployment guide (manual).
- 9.4. Create user manual for dashboard.

### 10. Deployment & Operations
- 10.1. Configure VPS (Ubuntu) – install Python, dependencies, cron.
- 10.2. Transfer code and set up environment variables.
- 10.3. Initialize database and run migrations.
- 10.4. Start dashboard service (Streamlit) as systemd unit.
- 10.5. Test cron job manually.
- 10.6. Monitor first week, adjust settings.