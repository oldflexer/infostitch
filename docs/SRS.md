# Software Requirements Specification (SRS)
## News Aggregator & Publisher System

### 1. Introduction
**Purpose**: Automate collection, filtering, and publishing of AI/tech news from multiple RSS feeds to Telegram, VK, and Max platforms.

**Scope**: Internal tool for a single Telegram channel (@myaiqnews) and associated VK group and Max chat. Supports 8–10 posts per day with configurable schedule.

**Definitions**:
- **Pipeline** – sequential processing chain: RSS fetch → deduplication → selection → content extraction → post generation → publishing.
- **Embedding** – vector representation of text for semantic similarity (cosine distance).
- **Graceful degradation** – system continues functioning with limited features when external services are unavailable.

### 2. Functional Requirements

#### FR1: RSS Feed Management
- **FR1.1** System shall read a list of RSS feed URLs from database.
- **FR1.2** Each feed shall be fetched every execution cycle (configurable interval).
- **FR1.3** System shall extract: title, URL, publication date, snippet, and image (from enclosure/media/HTML).

#### FR2: Deduplication
- **FR2.1** Primary filter by URL (against `published_posts`).
- **FR2.2** Secondary filter by Jaccard similarity of titles (threshold configurable, default 0.55).
- **FR2.3** Final semantic check by cosine similarity of embeddings (threshold configurable, default 0.75) using pgvector.

#### FR3: Article Selection
- **FR3.1** System shall pass up to 20 deduplicated candidates to LLM (Gemini) for ranking.
- **FR3.2** LLM receives list of recent published titles to avoid topic duplicates.
- **FR3.3** LLM returns ordered list of selected article IDs (1..20).

#### FR4: Content Extraction
- **FR4.1** For each selected article, fetch full content via Jina AI Reader (https://r.jina.ai).
- **FR4.2** Extract main image (priority: RSS enclosure → Jina featured image → regex from Markdown).
- **FR4.3** Clean text: remove links, images, extra newlines, truncate to 6000 characters.

#### FR5: Post Generation
- **FR5.1** Choose post template from 10 predefined styles (with rotation history).
- **FR5.2** Generate post using LLM with strict guidelines:
  - Only facts from the article.
  - Length 700–730 characters (before adding source link and signature).
  - One emoji, one HTML `<b>` tag for emphasis.
  - No Markdown, no links, no channel signature.
- **FR5.3** Append source link and signature `Подготовлено каналом @myaiqnews`; truncate to 1000 symbols with HTML tag repair.

#### FR6: Publishing
- **FR6.1** Send to Telegram (photo if image exists, else text).
- **FR6.2** Send to VK (photo via upload server, else text).
- **FR6.3** Send to Max (text + image URL if available).
- **FR6.4** Each channel can be enabled/disabled via database.

#### FR7: Data Persistence
- **FR7.1** Store `published_posts` with: clean_url, title, summary, embedding (vector), created_at.
- **FR7.2** Store `rss_sources`, `channels`, `llm_models`, `settings`, `users` (for dashboard).
- **FR7.3** Support manual and automatic cleanup (older than N days).

#### FR8: Error Handling & Notifications
- **FR8.1** Retry failed external API calls (with exponential backoff).
- **FR8.2** Log all errors with structured JSON.
- **FR8.3** Send critical errors to designated Telegram chat (personal message from bot).

#### FR9: Dashboard (Streamlit)
- **FR9.1** View pipeline execution history and metrics.
- **FR9.2** View and filter logs.
- **FR9.3** Edit configuration (RSS sources, channels, LLM models, thresholds).
- **FR9.4** Manual trigger pipeline run.
- **FR9.5** Manual data cleanup.

### 3. Non-Functional Requirements

- **Performance**: Full pipeline cycle < 2 minutes for 20 articles.
- **Reliability**: System continues on partial failures; detailed logs for debugging.
- **Maintainability**: Modular DDD architecture with DI; easy to replace DB, LLM, or publishing channels.
- **Security**: API keys stored in environment variables or encrypted DB fields.
- **Scalability**: Designed to handle up to 50 RSS feeds and multiple channels.
- **Platform**: Runs on Ubuntu (production) and Windows (development).

### 4. Constraints & Assumptions

- Python 3.13+.
- SQLite initially, PostgreSQL with pgvector later.
- External services: Google Gemini API, Jina AI, Telegram Bot API, VK API, Max platform.
- No real-time requirements.

### 5. Use Cases
(High-level)
1. User configures RSS sources and channels via dashboard.
2. Cron triggers pipeline every N hours.
3. System fetches articles, deduplicates, selects top candidates.
4. For each candidate, generates and publishes post.
5. Errors are logged and notified.
6. Admin monitors dashboard and adjusts settings.