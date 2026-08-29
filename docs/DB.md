# Database Schema (DB)
## News Aggregator & Publisher System

### 1. Overview

| Aspect | Detail |
|--------|--------|
| **Database (Dev)** | SQLite 3 (file-based, zero-config) |
| **Database (Prod)** | PostgreSQL 16+ with `pgvector` extension |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Migrations** | Alembic |
| **Naming Convention** | snake_case for tables/columns, plural table names |
| **Primary Keys** | `id` (BigInteger, autoincrement) |
| **Timestamps** | `created_at` (DateTime, UTC, server_default=now()), `updated_at` where applicable |
| **Soft Deletes** | Not used; hard deletes with retention policies |

> **AD5**: SQLite for initial development with abstraction; PostgreSQL in production for `pgvector` support.

---

### 2. Entity-Relationship Diagram

```mermaid
erDiagram
    RSS_SOURCES ||--o{ PUBLISHED_POSTS : "fetches > publishes"
    CHANNELS ||--o{ PUBLISHED_POSTS : "publishes to"
    LLM_MODELS ||--o{ PUBLISHED_POSTS : "generates with"
    SETTINGS }|--|| RSS_SOURCES : "configures"
    SETTINGS }|--|| CHANNELS : "configures"
    SETTINGS }|--|| LLM_MODELS : "configures"
    USERS ||--o{ LOGS : "actions logged"

    RSS_SOURCES {
        bigint id PK
        varchar url UK
        boolean enabled
        datetime last_fetch
---

### 3. Table Definitions

#### 3.1 `rss_sources` — RSS Feed Configurations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `BIGINT` | `PK`, autoincrement | Surrogate key |
| `url` | `VARCHAR(500)` | `NOT NULL`, `UNIQUE` | RSS feed URL (validated) |
| `enabled` | `BOOLEAN` | `NOT NULL`, `DEFAULT true` | Toggle feed on/off |
| `last_fetch` | `DATETIME` | `NULLABLE` | Last successful fetch timestamp (UTC) |
| `created_at` | `DATETIME` | `NOT NULL`, `DEFAULT now()` | Record creation time |

**Indexes:**
- `ix_rss_sources_url` (UNIQUE) — on `url`
- `ix_rss_sources_enabled` — on `enabled` (partial: `WHERE enabled = true`)

**Referenced by:** `published_posts.source_id` (FK, see below — optional, for traceability)

> **SRS FR1.1, FR1.2**: System reads RSS URLs from DB, fetches each every cycle.

---

#### 3.2 `channels` — Publishing Destinations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `BIGINT` | `PK`, autoincrement | Surrogate key |
| `name` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE` | Human-readable name (e.g., "Telegram @myaiqnews") |
| `type` | `VARCHAR(20)` | `NOT NULL` | Enum: `telegram`, `vk`, `max` |
| `enabled` | `BOOLEAN` | `NOT NULL`, `DEFAULT true` | Toggle channel on/off |
| `config_json` | `JSONB` (PG) / `JSON` (SQLite) | `NOT NULL` | Channel-specific config (see below) |
| `created_at` | `DATETIME` | `NOT NULL`, `DEFAULT now()` | Record creation time |

**`config_json` Structure by Type:**

| Type | Required Keys | Example |
|------|---------------|---------|
| `telegram` | `chat_id`, `bot_token_ref` | `{"chat_id": "-1001234567890", "bot_token_ref": "TELEGRAM_BOT_TOKEN"}` |
| `vk` | `group_id`, `access_token_ref`, `album_id` (optional) | `{"group_id": "123456", "access_token_ref": "VK_TOKEN", "album_id": "789"}` |
| `max` | `chat_id`, `bot_token_ref` | `{"chat_id": "max_chat_123", "bot_token_ref": "MAX_BOT_TOKEN"}` |

> **SRS FR6.1–FR6.4**: Each channel can be enabled/disabled via DB.

**Indexes:**
- `ix_channels_type_enabled` — on `(type, enabled)` (partial: `WHERE enabled = true`)

---

#### 3.3 `llm_models` — LLM Provider Configurations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `BIGINT` | `PK`, autoincrement | Surrogate key |
| `name` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE` | Internal name (e.g., "gemini-1.5-flash") |
| `provider` | `VARCHAR(30)` | `NOT NULL` | Enum: `gemini`, `openai`, `anthropic`, `custom` |
| `model_id` | `VARCHAR(100)` | `NOT NULL` | Provider model identifier (e.g., `gemini-1.5-flash-latest`) |
| `api_key_ref` | `VARCHAR(100)` | `NOT NULL` | Reference to secret in `.env` or secret manager (e.g., `GEMINI_API_KEY_1`) |
| `is_active` | `BOOLEAN` | `NOT NULL`, `DEFAULT true` | Toggle model availability |
| `created_at` | `DATETIME` | `NOT NULL`, `DEFAULT now()` | Record creation time |

**Indexes:**
- `ix_llm_models_provider_active` — on `(provider, is_active)` (partial: `WHERE is_active = true`)

> **AD3**: DI allows swapping implementations; `api_key_ref` avoids hardcoding secrets (AD10).
        datetime created_at
    }
    CHANNELS {
        bigint id PK
        varchar name
        varchar type
        boolean enabled
        json config_json
        datetime created_at
    }
    LLM_MODELS {
        bigint id PK
        varchar name
        varchar provider
        varchar model_id
        varchar api_key_ref
        boolean is_active
        datetime created_at
    }
    SETTINGS {
        varchar key PK
        text value
        text description
    }
    PUBLISHED_POSTS {
        bigint id PK
---

#### 3.4 `settings` — Dynamic Configuration (Key-Value Store)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `key` | `VARCHAR(100)` | `PK` | Setting identifier (snake_case) |
| `value` | `TEXT` | `NOT NULL` | JSON-encoded value (string, number, bool, array, object) |
| `description` | `TEXT` | `NULLABLE` | Human-readable description |
| `updated_at` | `DATETIME` | `NOT NULL`, `DEFAULT now()` ON UPDATE | Last modification time |

**Predefined Settings (Seed Data):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `pipeline_interval_hours` | `int` | `3` | Cron interval (also used by scheduler) |
| `max_articles_per_run` | `int` | `20` | Max candidates passed to LLM selection |
| `jaccard_threshold` | `float` | `0.55` | Title similarity threshold (stage 1 dedup) |
| `embedding_similarity_threshold` | `float` | `0.75` | Cosine similarity threshold (stage 2 dedup) |
| `embedding_model` | `string` | `"text-embedding-004"` | Gemini embedding model |
| `post_length_min` | `int` | `700` | Min post length (chars, before link+signature) |
| `post_length_max` | `int` | `730` | Max post length (chars, before link+signature) |
| `post_total_max_length` | `int` | `1000` | Max total length after link+signature |
| `dedup_window_days_stage1` | `int` | `7` | Days to look back for Jaccard dedup |
| `dedup_window_days_stage2` | `int` | `5` | Days to look back for embedding dedup |
| `template_pool` | `array[string]` | `[...]` | List of 10 template IDs (see §6) |
| `default_template_id` | `string` | `"news_brief"` | Fallback template |
| `jina_api_key_ref` | `string` | `"JINA_API_KEY"` | Env var name for Jina AI |
| `notification_chat_id` | `string` | `""` | Admin Telegram chat for error alerts |
| `cleanup_retention_days` | `int` | `90` | Auto-delete published_posts older than N days |

> **AD4**: All configurable parameters in `settings` table; read on each pipeline run.

---

#### 3.5 `published_posts` — Published Articles with Embeddings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `BIGINT` | `PK`, autoincrement | Surrogate key |
| `clean_url` | `VARCHAR(500)` | `NOT NULL`, `UNIQUE` | Normalized URL (dedup key) |
| `title` | `VARCHAR(500)` | `NOT NULL` | Article title |
| `summary` | `TEXT` | `NOT NULL` | LLM-generated summary (used for embedding) |
| `embedding` | `VECTOR(768)` (PG) / `BLOB` (SQLite) | `NOT NULL` | Vector embedding of `title + summary` |
| `is_duplicate` | `BOOLEAN` | `NOT NULL`, `DEFAULT false` | Flagged by stage 2 dedup |
| `source_id` | `BIGINT` | `FK → rss_sources(id)`, `NULLABLE` | Origin RSS source (optional traceability) |
| `channel_id` | `BIGINT` | `FK → channels(id)`, `NULLABLE` | Primary publish channel (optional) |
| `llm_model_id` | `BIGINT` | `FK → llm_models(id)`, `NULLABLE` | Model used for generation |
| `template_id` | `VARCHAR(50)` | `NULLABLE` | Template used (from pool) |
| `post_text` | `TEXT` | `NULLABLE` | Full generated post text (for audit) |
| `image_url` | `VARCHAR(500)` | `NULLABLE` | Extracted article image URL |
| `created_at` | `DATETIME` | `NOT NULL`, `DEFAULT now()` | Publication timestamp |

**Indexes:**
- `ix_published_posts_clean_url` (UNIQUE) — on `clean_url` (primary dedup key)
- `ix_published_posts_created_at` — on `created_at DESC` (recent-first queries)
- `ix_published_posts_is_duplicate` — on `is_duplicate` (partial: `WHERE is_duplicate = false`)
- **PG only**: `ix_published_posts_embedding` — HNSW index on `embedding` (`vector_cosine_ops`) for fast similarity search

**Foreign Keys:**
- `fk_published_posts_source` → `rss_sources(id)` ON DELETE SET NULL
- `fk_published_posts_channel` → `channels(id)` ON DELETE SET NULL
- `fk_published_posts_llm_model` → `llm_models(id)` ON DELETE SET NULL

> **SRS FR2.1, FR2.3, FR7.1**: URL primary key prevents duplicate publish; embedding enables semantic dedup.
        varchar clean_url UK
        varchar title
        text summary
        vector embedding
        boolean is_duplicate
        datetime created_at
    }
    USERS {
        bigint id PK
        varchar username UK
        varchar password_hash
        varchar role
        datetime created_at
    }
    LOGS {
---

### 4. PostgreSQL-Specific: `pgvector` Setup

```sql
-- Run once on PostgreSQL database (superuser)
CREATE EXTENSION IF NOT EXISTS vector;

-- HNSW index for fast cosine similarity search (created after table)
CREATE INDEX ix_published_posts_embedding_hnsw
ON published_posts
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64)
WHERE is_duplicate = false;
```

**Similarity Query (Stage 2 Dedup):**
```sql
SELECT id, title, 1 - (embedding <=> $1) AS similarity
FROM published_posts
WHERE is_duplicate = false
  AND created_at > NOW() - INTERVAL '5 days'
ORDER BY embedding <=> $1
LIMIT 1;
```
Returns most similar post; if `similarity > 0.75` → duplicate.
---

#### 3.6 `users` — Dashboard Authentication

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `BIGINT` | `PK`, autoincrement | Surrogate key |
| `username` | `VARCHAR(50)` | `NOT NULL`, `UNIQUE` | Login username |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | Bcrypt hash (cost ≥ 12) |
| `role` | `VARCHAR(20)` | `NOT NULL`, `DEFAULT 'admin'` | Enum: `admin`, `viewer` |
| `created_at` | `DATETIME` | `NOT NULL`, `DEFAULT now()` | Account creation time |
| `last_login` | `DATETIME` | `NULLABLE` | Last successful login |

**Indexes:**
---

### 5. Alembic Migration Strategy

#### 5.1 Initial Migration (`versions/xxxx_initial_schema.py`)

```python
"""Initial schema

Revision ID: xxxx
Revises:
Create Date: 2026-08-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'xxxx'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # rss_sources
    op.create_table(
        'rss_sources',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('last_fetch', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url', name='uq_rss_sources_url'),
    )
    op.create_index('ix_rss_sources_enabled', 'rss_sources', ['enabled'], postgresql_where=sa.text('enabled = true'))

    # channels
    op.create_table(
        'channels',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_channels_name'),
    )
    op.create_index('ix_channels_type_enabled', 'channels', ['type', 'enabled'], postgresql_where=sa.text('enabled = true'))
```
- `ix_users_username` (UNIQUE) — on `username`

> **SRS FR9, HLD §7**: Dashboard auth via bcrypt.

---

#### 3.7 `logs` — Structured Application Logs (Optional)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `BIGINT` | `PK`, autoincrement | Surrogate key |
| `timestamp` | `DATETIME` | `NOT NULL`, `DEFAULT now()` | Log timestamp (UTC) |
| `level` | `VARCHAR(10)` | `NOT NULL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `module` | `VARCHAR(100)` | `NOT NULL` | Python module (e.g., `pipeline.steps.fetch_rss`) |
| `message` | `TEXT` | `NOT NULL` | Human-readable message |
| `context_json` | `JSONB` / `JSON` | `NULLABLE` | Structured context (correlation_id, duration_ms, etc.) |
| `user_id` | `BIGINT` | `FK → users(id)`, `NULLABLE` | Acting user (for dashboard actions) |

**Indexes:**
- `ix_logs_timestamp` — on `timestamp DESC`
#### 5.1.1 Initial Migration (continued)

```python
    # llm_models
    op.create_table(
#### 5.1.2 Initial Migration (continued)

```python
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='admin'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username', name='uq_users_username'),
    )

    # logs
    op.create_table(
        'logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('level', sa.String(10), nullable=False),
        sa.Column('module', sa.String(100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('context_json', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_logs_timestamp', 'logs', ['timestamp'], postgresql_using='btree', postgresql_ops={'timestamp': 'DESC'})
    op.create_index('ix_logs_level', 'logs', ['level'])
    op.create_index('ix_logs_module', 'logs', ['module'])

def downgrade() -> None:
    op.drop_table('logs')
    op.drop_table('users')
    op.drop_table('published_posts')
    op.drop_table('settings')
    op.drop_table('llm_models')
    op.drop_table('channels')
    op.drop_table('rss_sources')
```

#### 5.2 Migration Commands

```bash
# Generate initial migration
alembic revision --autogenerate -m "initial_schema"

# Apply migrations
---

### 6. Seed Data (Run After Migration)

```python
# scripts/seed.py
import json
from sqlalchemy.orm import Session
from src.infrastructure.db.sqlalchemy_models import (
    RssSource, Channel, LLMModel, Setting, User
)
from src.infrastructure.db.session import engine
from passlib.hash import bcrypt

def seed(db: Session):
    # Settings
    settings = [
        Setting(key="pipeline_interval_hours", value="3", description="Cron interval in hours"),
        Setting(key="max_articles_per_run", value="20", description="Max candidates for LLM selection"),
        Setting(key="jaccard_threshold", value="0.55", description="Title Jaccard similarity threshold"),
        Setting(key="embedding_similarity_threshold", value="0.75", description="Cosine similarity threshold for embeddings"),
        Setting(key="embedding_model", value="text-embedding-004", description="Gemini embedding model"),
        Setting(key="post_length_min", value="700", description="Min post length before link+signature"),
        Setting(key="post_length_max", value="730", description="Max post length before link+signature"),
        Setting(key="post_total_max_length", value="1000", description="Max total length after link+signature"),
        Setting(key="dedup_window_days_stage1", value="7", description="Days for Jaccard dedup lookback"),
        Setting(key="dedup_window_days_stage2", value="5", description="Days for embedding dedup lookback"),
        Setting(key="template_pool", value=json.dumps([
            "news_brief", "deep_dive", "quick_take", "expert_opinion",
            "case_study", "trend_analysis", "tool_review", "research_summary",
            "industry_news", "tutorial_style"
        ]), description="Available template IDs"),
        Setting(key="default_template_id", value="news_brief", description="Fallback template"),
        Setting(key="jina_api_key_ref", value="JINA_API_KEY", description="Env var for Jina AI API key"),
        Setting(key="notification_chat_id", value="", description="Admin Telegram chat ID for alerts"),
        Setting(key="cleanup_retention_days", value="90", description="Auto-delete posts older than N days"),
    ]
    db.add_all(settings)

    # Default admin user (password: change_me_123)
    admin = User(
        username="admin",
        password_hash=bcrypt.hash("change_me_123"),
        role="admin"
---

### 7. SQLAlchemy Model Mapping (Reference)

```python
# src/infrastructure/db/sqlalchemy_models.py
from sqlalchemy import BigInteger, String, Boolean, DateTime, Text, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import VECTOR
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class RssSource(Base):
    __tablename__ = 'rss_sources'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_fetch: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class Channel(Base):
    __tablename__ = 'channels'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # telegram, vk, max
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class LLMModel(Base):
    __tablename__ = 'llm_models'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    api_key_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class Setting(Base):
    __tablename__ = 'settings'
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class PublishedPost(Base):
    __tablename__ = 'published_posts'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    clean_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(768), nullable=False)  # PG; LargeBinary for SQLite
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_id: Mapped[int | None] = mapped_column(ForeignKey('rss_sources.id', ondelete='SET NULL'), nullable=True)
    channel_id: Mapped[int | None] = mapped_column(ForeignKey('channels.id', ondelete='SET NULL'), nullable=True)
    llm_model_id: Mapped[int | None] = mapped_column(ForeignKey('llm_models.id', ondelete='SET NULL'), nullable=True)
    template_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    post_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    source: Mapped["RssSource"] = relationship(backref="published_posts")
    channel: Mapped["Channel"] = relationship(backref="published_posts")
    llm_model: Mapped["LLMModel"] = relationship(backref="published_posts")

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="admin", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
---

### 8. SQLite vs PostgreSQL Differences

| Feature | SQLite (Dev) | PostgreSQL (Prod) |
|---------|--------------|-------------------|
| `embedding` column | `BLOB` (pickled `list[float]`) | `VECTOR(768)` |
| Similarity search | Python-side (load all, compute cosine) | `pgvector` HNSW index (server-side) |
| `config_json`, `context_json` | `JSON` (text) | `JSONB` (binary, indexed) |
| `DATETIME` timezone | Stored as UTC text | `TIMESTAMPTZ` |
| Concurrent writes | Limited (WAL mode) | Full MVCC |
| `ON UPDATE` trigger | Manual / application-level | Native `ON UPDATE CURRENT_TIMESTAMP` |

**Abstraction:** Repository layer hides differences; `EmbeddingRepository` has `find_similar()` with PG/SQLite implementations.

---

### 9. Retention & Cleanup

```sql
-- Manual cleanup (run via CLI or cron)
DELETE FROM published_posts
WHERE created_at < NOW() - INTERVAL '90 days';

-- Or via settings: cleanup_retention_days
```

> **SRS FR7.3**: Manual and automatic cleanup supported.

---

### 10. Security Notes

- **No secrets in DB**: `api_key_ref`, `bot_token_ref` point to environment variables or secret manager
- **Passwords**: Bcrypt (cost ≥ 12), never plaintext
- **Least privilege**: DB user for app has `SELECT, INSERT, UPDATE` on app tables only; no `DROP`, `ALTER`
- **Audit trail**: `logs` table captures dashboard actions with `user_id`

---

### 11. Future Extensions

| Table | Purpose | Trigger |
|-------|---------|---------|
| `post_templates` | Store template prompts in DB (not code) | When template pool > 10 or needs runtime editing |
| `pipeline_runs` | Execution history (status, duration, counts) | For dashboard metrics |
| `article_candidates` | Raw fetched articles before dedup | For debugging/analysis |
| `channel_posts` | Many-to-many: post × channel (per-channel status) | When per-channel retry/logic needed |

---

*Generated from SRS, HLD, AD, PBS. Keep in sync with `sqlalchemy_models.py` and Alembic migrations.*
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    level: Mapped[str] = mapped_column(String(10), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
```
    )
    db.add(admin)

    db.commit()
```
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "add_column_xyz"

# Rollback
alembic downgrade -1
```
        'llm_models',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('provider', sa.String(30), nullable=False),
        sa.Column('model_id', sa.String(100), nullable=False),
        sa.Column('api_key_ref', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_llm_models_name'),
    )
    op.create_index('ix_llm_models_provider_active', 'llm_models', ['provider', 'is_active'], postgresql_where=sa.text('is_active = true'))

    # settings
    op.create_table(
        'settings',
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('key'),
    )

    # published_posts
    op.create_table(
        'published_posts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('clean_url', sa.String(500), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('embedding', postgresql.VECTOR(768), nullable=False),
        sa.Column('is_duplicate', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('source_id', sa.BigInteger(), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), nullable=True),
        sa.Column('llm_model_id', sa.BigInteger(), nullable=True),
        sa.Column('template_id', sa.String(50), nullable=True),
        sa.Column('post_text', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clean_url', name='uq_published_posts_clean_url'),
        sa.ForeignKeyConstraint(['source_id'], ['rss_sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['llm_model_id'], ['llm_models.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_published_posts_created_at', 'published_posts', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    op.create_index('ix_published_posts_is_duplicate', 'published_posts', ['is_duplicate'], postgresql_where=sa.text('is_duplicate = false'))
```
- `ix_logs_level` — on `level`
- `ix_logs_module` — on `module`

> **AD7**: Structured JSON logging; DB storage optional (can use file/stdout + Prometheus).
        bigint id PK
        datetime timestamp
        varchar level
        text message
        json context_json
    }
```