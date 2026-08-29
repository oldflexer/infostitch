# Product Breakdown Structure (PBS)
## News Aggregator & Publisher System

### 1. Overview
This document defines the hierarchical decomposition of the final product into its constituent components and modules. It describes **what** the system consists of, not **how** it is built (that is covered by WBS).

The system is divided into the following top‑level subsystems:

1. **Core Domain** – business logic and data models.
2. **Pipeline Engine** – the processing sequence.
3. **Infrastructure Services** – external integrations and utilities.
4. **Presentation Layer** – user interfaces (CLI and dashboard).
5. **Data Storage** – persistence layer.
6. **Observability** – logging, metrics, and monitoring.
7. **Configuration & Administration** – runtime settings and management.

---

### 2. Subsystem Breakdown

#### 2.1. Core Domain
- **Entities**:
  - `Article` – raw article from RSS.
  - `Post` – final published post (including generated text, summary, embedding).
  - `RssSource` – RSS feed configuration.
  - `Channel` – publishing destination (Telegram, VK, Max, etc.).
  - `Template` – post style template.
  - `User` – dashboard user.
- **Value Objects**:
  - `URL` – validated and normalized URL.
  - `Embedding` – vector representation.
  - `TemplateId` – identifier for template selection.
- **Domain Services**:
  - `DeduplicationService` – logic for duplicate detection.
  - `TemplateSelector` – logic for choosing template (random with history).
  - `PostComposer` – combines generated text with source link and signature.

#### 2.2. Pipeline Engine
- **Pipeline Orchestrator** – executes steps in order.
- **Steps** (each implements `PipelineStep` interface):
  1. `FetchRSSStep` – fetches and normalizes RSS.
  2. `DeduplicateStep1` – filters by URL and Jaccard similarity.
  3. `SelectTopStep` – calls LLM to rank candidates.
  4. `ExtractContentStep` – fetches full article (Jina AI), extracts image.
  5. `GeneratePostStep` – selects template, calls LLM to generate post.
  6. `ComputeEmbeddingStep` – generates embedding for `title + summary`.
  7. `DeduplicateStep2` – semantic check against recent posts.
  8. `PublishStep` – sends post to all enabled channels.
- **Pipeline Context** – shared data passed between steps (articles, selected IDs, generated content, etc.).

#### 2.3. Infrastructure Services
- **LLM Client** – abstraction over LLM providers (Gemini, optionally others).
- **Embedding Client** – specific endpoints for embeddings (may reuse LLM client).
- **Content Extractor Client** – Jina AI reader.
- **Publishing Clients**:
  - `TelegramClient` – sendPhoto, sendMessage.
  - `VKClient` – upload photo and wall post.
  - `MaxClient` – send message to chat.
- **Cache Service** – in-memory TTL cache for API responses.
- **Retry & Circuit Breaker** – for resilient external calls.
- **Notification Service** – sends error alerts to admin's Telegram.

#### 2.4. Presentation Layer
- **Command‑Line Interface (CLI)**:
  - `run` – execute pipeline once.
  - `clear` – manual cleanup of old records.
  - `config` – view/edit settings (via CLI).
- **Streamlit Dashboard**:
  - **Authentication** – login page.
  - **Overview Page** – pipeline status, last run, quick stats.
  - **Logs Page** – filterable log viewer.
  - **Settings Page** – manage RSS sources, channels, LLM models, thresholds.
  - **Metrics Page** – charts for pipeline duration, success rates, API usage.
  - **Manual Actions** – trigger pipeline, clear old data.

#### 2.5. Data Storage
- **Relational Database** (SQLite/PostgreSQL):
  - Tables: `rss_sources`, `channels`, `llm_models`, `settings`, `published_posts`, `users`, `logs` (optional).
- **Repository Layer**:
  - Interfaces for each entity (e.g., `ArticleRepository`, `PostRepository`, `SourceRepository`).
  - SQLAlchemy implementations.
- **Migrations** – Alembic scripts for schema evolution.

#### 2.6. Observability
- **Structured Logging** – JSON logs with consistent fields.
- **Metrics** – Prometheus counters/histograms:
  - Pipeline duration per step.
  - Success/failure counts per step and channel.
  - API call counts and latencies.
  - Number of processed/filtered/published articles.
- **Alerting** – (optional) integrate with Prometheus Alertmanager or simply send notifications via Notification Service.

#### 2.7. Configuration & Administration
- **Configuration Sources**:
  - Environment variables (secrets, environment type).
  - Database tables (`settings`, `rss_sources`, `channels`, `llm_models`).
- **Admin Features**:
  - Dynamic reconfiguration (no restart).
  - Manual override of thresholds.
  - Enable/disable channels on the fly.
  - Historical data retention policy.

---

### 3. Component Dependencies (High-Level)
```
┌─────────────────────────────────────────────────────────────────┐
│ Presentation (CLI + Dashboard) │
└───────────────────────────┬─────────────────────────────────┘
│
┌───────────────────────────▼─────────────────────────────────┐
│ Pipeline Engine & Core Domain │
│ Orchestrator, Steps, Domain Services, Entities, VOs │
└─────────────┬───────────────────────────────┬─────────────┘
│ │
┌─────────────▼─────────────┐ ┌─────────────▼─────────────┐
│ Infrastructure Services │ │ Data Storage (Repos + │
│ (LLM, Embedding, Jina, │ │ DB Clients) │
│ Channels, Cache, Retry) │ │ │
└─────────────────────────────┘ └─────────────────────────────┘
│ │
┌─────────────▼─────────────┐ ┌─────────────▼─────────────┐
│ External APIs │ │ SQLite / PostgreSQL │
│ (Gemini, Jina, Telegram,│ │ (with pgvector ext) │
│ VK, Max) │ │ │
└─────────────────────────────┘ └─────────────────────────────┘
```

---

### 4. Module Ownership (for future teams)
Not applicable (single developer), but can be assigned per module.

---

### 5. Traceability
This PBS aligns with SRS and HLD. Each component listed here appears in the architecture diagrams and serves one or more functional requirements.

| Component            | Related FR(s)            |
|----------------------|---------------------------|
| Core Domain          | All (business logic)     |
| Pipeline Steps       | FR1–FR6                  |
| LLM/Embedding Clients| FR3, FR5, FR7            |
| Content Extractor    | FR4                      |
| Publishing Clients   | FR6                      |
| Dashboard            | FR9                      |
| Observability        | FR8, NFRs                |