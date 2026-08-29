infostitch/
├── alembic/                      # миграции БД
├── docs/                         # документация (SRS, HLD, AD, etc.)
├── src/
│   ├── domain/                   # DDD – сущности, value objects, агрегаты
│   │   ├── entities/
│   │   │   ├── article.py
│   │   │   ├── post.py
│   │   │   ├── rss_source.py
│   │   │   └── channel.py
│   │   ├── value_objects/
│   │   │   ├── url.py
│   │   │   ├── embedding.py
│   │   │   └── template.py
│   │   └── repositories/         # интерфейсы
│   │       ├── article_repo.py
│   │       ├── post_repo.py
│   │       ├── source_repo.py
│   │       └── setting_repo.py
│   ├── application/              # Use Cases, сервисы
│   │   ├── pipeline/             # конвейер обработки
│   │   │   ├── steps/
│   │   │   │   ├── fetch_rss.py
│   │   │   │   ├── deduplicate.py
│   │   │   │   ├── select_top.py
│   │   │   │   ├── extract_content.py
│   │   │   │   ├── generate_post.py
│   │   │   │   ├── check_embedding_duplicate.py
│   │   │   │   └── publish.py
│   │   │   └── pipeline.py       # оркестратор
│   │   ├── services/             # бизнес-логика
│   │   │   ├── llm_service.py    # абстракция для LLM
│   │   │   ├── embedding_service.py
│   │   │   ├── image_service.py
│   │   │   └── publisher_service.py # публикация в каналы
│   │   └── dto/                  # Data Transfer Objects
│   ├── infrastructure/            # реализации
│   │   ├── db/
│   │   │   ├── sqlalchemy_models.py
│   │   │   ├── repositories/     # конкретные репозитории
│   │   │   └── session.py
│   │   ├── clients/              # внешние API
│   │   │   ├── gemini_client.py
│   │   │   ├── jina_client.py
│   │   │   ├── telegram_client.py
│   │   │   ├── vk_client.py
│   │   │   └── max_client.py
│   │   ├── cache/                # кэширование
│   │   │   └── cache_service.py
│   │   └── logging/              # структурированные логи + метрики
│   │       ├── logger.py
│   │       └── metrics.py
│   └── presentation/
│       ├── cli/                  # скрипт для запуска пайплайна
│       │   └── run.py
│       └── dashboard/            # Streamlit
│           ├── app.py
│           └── pages/
│               ├── overview.py
│               ├── logs.py
│               ├── settings.py
│               └── metrics.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                      # вспомогательные (миграции, очистка)
├── .env.example
├── requirements.txt
├── pyproject.toml                # для poetry или pip
└── README.md