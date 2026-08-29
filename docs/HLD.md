# High-Level Design (HLD)
## News Aggregator & Publisher System

### 1. System Overview
The system is a batch-processing pipeline that runs periodically. It consists of four logical layers:

- **Domain Layer** – business entities and rules.
- **Application Layer** – use cases (pipeline steps, services).
- **Infrastructure Layer** – external dependencies (DB, APIs, cache, logging).
- **Presentation Layer** – CLI and Streamlit dashboard.

All layers communicate through interfaces (Dependency Inversion).

### 2. Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION │
│ ┌──────────────┐ ┌───────────────────────┐ │
│ │ CLI (cron) │ │ Streamlit Dashboard │ │
│ └──────────────┘ └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Pipeline Orchestrator │ │
│ │ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ │ │
│ │ │Step 1 │→│Step 2 │→│... │→│Step N │ │ │
│ │ │Fetch RSS│ │Dedup │ │Generate │ │Publish │ │ │
│ │ └─────────┘ └──────────┘ └─────────┘ └─────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Services (Use Cases) │ │
│ │ LLM, Embedding, Image, Publisher, Cache, Logger │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE │
│ ┌──────────┐ ┌─────────┐ ┌────────┐ ┌─────────┐ ┌─────┐ │
│ │ Repos │ │ Clients │ │ Cache │ │ Logger │ │Metrics│ │
│ │(SQLAlch.)│ │(HTTP) │ │(in- │ │(struct- │ │(Prom) │ │
│ │ │ │ │ │memory)│ │log) │ │ │ │
│ └──────────┘ └─────────┘ └────────┘ └─────────┘ └─────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ DOMAIN │
│ Entities: Article, Post, RssSource, Channel, Template │
│ Value Objects: URL, Embedding, TemplateId │
│ Repository Interfaces │
└─────────────────────────────────────────────────────────────┘
```


### 3. Data Flow (Pipeline)

1. **Fetch RSS** → Reads `rss_sources` from DB, fetches each feed, normalizes data.
2. **Deduplicate (stage 1)** → Filters by URL and Jaccard similarity (against last 7 days).
3. **Select Top** → Passes up to 20 candidates + recent titles to Gemini, gets ordered list of IDs.
4. **Loop over selected IDs** (each iteration):
   - **Extract Content** → Jina AI → clean text + extract image.
   - **Choose Template** → picks random from 10 (with history).
   - **Generate Post** → LLM with template instructions → returns post_text and summary.
   - **Compute Embedding** → calls Gemini embedding for `title + summary`.
   - **Check Duplicate (stage 2)** → queries DB for most similar post in last 5 days; if similarity > 0.75 → skip publishing, save as duplicate.
   - **Publish** → if not duplicate:
        - Send to enabled channels (Telegram, VK, Max) with photo if available.
        - Save to `published_posts` with embedding.
        - If publishing fails, log error and continue (graceful degradation).

### 4. Database Schema (simplified)

- **rss_sources** (id, url, enabled, last_fetch, created_at)
- **channels** (id, name, type, enabled, config_json) — e.g., telegram_chat_id, vk_group_id, max_chat_id.
- **llm_models** (id, name, provider, model_id, api_key_ref, is_active)
- **settings** (key, value, description) — thresholds, intervals, template pool.
- **published_posts** (id, clean_url, title, summary, embedding, created_at, is_duplicate)
- **users** (id, username, password_hash, role) — for dashboard auth.
- **logs** (id, timestamp, level, message, context_json) — optional.

### 5. Integration Points

- **Google Gemini**: for selection, generation, and embeddings.
- **Jina AI**: for content extraction.
- **Telegram Bot API**: sendPhoto, sendMessage.
- **VK API**: photos.getWallUploadServer → upload → save → wall.post.
- **Max API**: POST /messages with chat_id.

### 6. Error Handling Strategy

- **Retry** with exponential backoff (3 attempts) for HTTP requests.
- **Circuit breaker** for repeated failures (optional).
- On non-critical failures (e.g., image download), continue with fallback (text-only).
- All exceptions caught and logged; if pipeline step fails, the whole cycle is aborted but notification sent.

### 7. Security

- Secrets not hardcoded; stored in `.env` or encrypted in DB.
- Dashboard authentication via bcrypt hashed passwords.