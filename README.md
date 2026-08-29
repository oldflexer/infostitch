# InfoStitch - News Aggregator & Publisher System

Automated collection, filtering, and publishing of AI/tech news from multiple RSS feeds to Telegram, VK, and Max platforms.

## Features

- **RSS Aggregation**: Fetches from multiple configurable RSS sources
- **Smart Deduplication**: URL-based, Jaccard similarity, and semantic (embedding) deduplication
- **AI-Powered Selection**: Uses LLM (Gemini) to rank and select best articles
- **Content Extraction**: Full article extraction via Jina AI Reader
- **Template-Based Generation**: 10 predefined post templates with rotation
- **Multi-Channel Publishing**: Telegram, VK, and Max (Odnoklassniki)
- **Admin Dashboard**: Streamlit-based UI for monitoring and configuration
- **Structured Logging**: JSON logs with correlation IDs
- **Metrics**: Prometheus metrics for monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION │
│ ┌──────────────┐ ┌───────────────────────┐ │
│ │ CLI (cron)   │ │ Streamlit Dashboard   │ │
│ └──────────────┘ └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Pipeline Orchestrator                               │ │
│ │ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐  │ │
│ │ │Fetch RSS│→│Dedup 1   │→│Select   │→│Extract  │  │ │
│ │ └─────────┘ └──────────┘ └─────────┘ └─────────┘  │ │
│ │ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐  │ │
│ │ │Generate │→│Embedding │→│Dedup 2  │→│Publish  │  │ │
│ │ └─────────┘ └──────────┘ └─────────┘ └─────────┘  │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE │
│ ┌──────────┐ ┌─────────┐ ┌────────┐ ┌─────────┐ ┌─────┐   │
│ │ Repos    │ │ Clients │ │ Cache  │ │ Logger  │ │Metrics│  │
│ │(SQLAlch.)│ │(HTTP)   │ │(mem)   │ │(struct) │ │(Prom) │  │
│ └──────────┘ └─────────┘ └────────┘ └─────────┘ └─────┘   │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ DOMAIN │
## Quick Start

### Prerequisites

- Python 3.13+
- SQLite (dev) or PostgreSQL 16+ with pgvector (prod)

### Installation

```bash
# Clone repository
git clone https://github.com/oldflexer/infostitch.git
cd infostitch

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` with your API keys:

```env
# Required
GEMINI_API_KEY=your_gemini_key
JINA_API_KEY=your_jina_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_channel_id

# Optional
VK_ACCESS_TOKEN=your_vk_token
VK_GROUP_ID=your_group_id
MAX_BOT_TOKEN=your_max_token
MAX_CHAT_ID=your_max_chat_id
```

### Database Setup

```bash
# Initialize database (creates tables)
python -m src.presentation.cli.run init-db

# Seed with defaults (RSS sources, channels, LLM models, admin user)
python -m src.presentation.cli.run seed
```

### Running the Pipeline

```bash
# Run once
python -m src.presentation.cli.run run

# Run with dry-run (no publishing)
## Project Structure

```
infostitch/
├── alembic/                      # Database migrations
├── docs/                         # Documentation (SRS, HLD, AD, etc.)
├── scripts/                      # Utility scripts (seed, etc.)
├── src/
│   ├── domain/                   # DDD - entities, value objects, repositories
│   ├── application/              # Use cases, services, pipeline
│   ├── infrastructure/           # Implementations (DB, clients, cache)
│   └── presentation/             # CLI and Streamlit dashboard
├── tests/                        # Unit, integration, E2E tests
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

## Documentation

- [SRS](docs/SRS.md) - Software Requirements Specification
- [HLD](docs/HLD.md) - High-Level Design
- [AD](docs/AD.md) - Architecture Decisions
- [DB](docs/DB.md) - Database Schema
- [ROADMAP](docs/ROADMAP.md) - Development Roadmap
- [WBS](docs/WBS.md) - Work Breakdown Structure
- [PBS](docs/PBS.md) - Product Breakdown Structure
- [TEST_PLAN](docs/TEST_PLAN.md) - Test Plan
- [QA_EVAL](docs/QA_EVAL.md) - QA Evaluation Strategy

## Development

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint
flake8 src tests

# Type check
mypy src

# Run tests
pytest tests/ -v --cov=src
```

### Adding a New Pipeline Step

1. Create step in `src/application/pipeline/steps/`
2. Implement `PipelineStep` interface
3. Register in `src/application/pipeline/pipeline.py`

### Adding a New Channel

1. Add client in `src/infrastructure/clients/`
2. Implement `PublisherClient` interface
3. Register in `src/application/services/publisher_service.py`

## License

MIT License - see LICENSE file for details.
python -m src.presentation.cli.run run --dry-run

# Clear old data
python -m src.presentation.cli.run clear --days 90

# Show configuration
python -m src.presentation.cli.run config
```

### Running the Dashboard

```bash
streamlit run src/presentation/dashboard/app.py
```

Then open http://localhost:8501

Default login: `admin` / `change_me_123` (change immediately!)

### Scheduling (Production)

Add to crontab for automatic runs every 3 hours:

```bash
0 */3 * * * /path/to/venv/bin/python -m src.presentation.cli.run run
```
│ Entities: Article, Post, RssSource, Channel, Template      │
│ Value Objects: URL, Embedding, TemplateId                   │
│ Repository Interfaces                                       │
└─────────────────────────────────────────────────────────────┘
```