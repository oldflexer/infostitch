# Development Roadmap
## News Aggregator & Publisher System

### Timeline: ~11 weeks (flexible)

---

### Iteration 0: Foundation (Week 1)
**Goal**: Project skeleton, DB schema, domain models.

- Create repo and structure.
- Setup Python environment and dependencies.
- Define SQLAlchemy models and generate Alembic migration.
- Define domain entities and repository interfaces.
- Implement basic config loader (from .env + DB).

---

### Iteration 1: Core Pipeline (Weeks 2–3)
**Goal**: End-to-end pipeline with mock clients.

- Implement all infrastructure clients (Gemini, Jina, Telegram, VK, Max) – initially with mocks.
- Implement services (LLM, Embedding, Content, Publisher).
- Implement each pipeline step (Fetch, Dedup, Select, Extract, Generate, Embed, Dedup2, Publish).
- Implement Pipeline Orchestrator.
- Implement CLI to run pipeline and save results to DB.
- Test with real RSS feeds (but mock publish).

---

### Iteration 2: Error Handling & Observability (Week 4)
**Goal**: Production-ready reliability.

- Add retry mechanism and graceful degradation.
- Implement structured logging (structlog) with correlation IDs.
- Add Prometheus metrics (pipeline_duration, step_success/fail, api_call_count).
- Implement error notification (Telegram personal message).
- Write first integration tests.

---

### Iteration 3: Dashboard (Weeks 5–6)
**Goal**: Admin UI for monitoring and configuration.

- Setup Streamlit app with login authentication.
- Overview page: pipeline status, recent runs, metrics charts.
- Logs page: search and filter.
- Settings page: CRUD for RSS sources, channels, LLM models, thresholds.
- Manual trigger and cleanup actions.
- Connect to Prometheus metrics (or read from DB).

---

### Iteration 4: Testing & Polish (Weeks 7–8)
**Goal**: High code quality and full test coverage.

- Write unit tests for all domain and service classes (≥80% coverage).
- Write integration tests for repositories and pipeline steps.
- Write E2E test using test configuration and mock APIs.
- Static analysis: flake8, mypy, black.
- Fix bugs and optimize performance.

---

### Iteration 5: Deployment & Stabilization (Weeks 9–10)
**Goal**: Production deployment and monitoring.

- Set up VPS (Ubuntu) with code, env, dependencies.
- Create systemd service for dashboard.
- Configure cron (every 3 hours).
- Run first real pipeline, verify published posts.
- Monitor logs and metrics for a week; fix issues.
- Write deployment guide and user manual.

---

### Iteration 6: Future Enhancements (ongoing)
- Switch to PostgreSQL+pgvector for faster similarity search.
- Add more LLM providers (Claude, OpenAI).
- Add more channels (Twitter, LinkedIn).
- Implement A/B testing for post templates.
- Add scheduled reports (weekly stats).