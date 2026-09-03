"""Test configuration and shared fixtures."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from infrastructure.config import Settings
from infrastructure.db.repositories.article_repo import SqlAlchemyArticleRepository
from infrastructure.db.repositories.channel_repo import SqlAlchemyChannelRepository
from infrastructure.db.repositories.llm_model_repo import SqlAlchemyLLMModelRepository
from infrastructure.db.repositories.log_repo import SqlAlchemyLogRepository
from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository
from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository
from infrastructure.db.repositories.user_repo import SqlAlchemyUserRepository
from infrastructure.db.sqlalchemy_models import Base
from infrastructure.db.sqlalchemy_models import (
    Channel as ChannelModel,
    LLMModel as LLMModelModel,
    PublishedPost as PublishedPostModel,
    RssSource as RssSourceModel,
    Setting as SettingModel,
    User as UserModel,
)

fake = Faker()


# ============================================================================
# Test Database Fixtures
# ============================================================================

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create in-memory SQLite test engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        app_env="test",
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="test-gemini-key",
        jina_api_key="test-jina-key",
        telegram_bot_token="test-telegram-token",
        telegram_chat_id="test-chat-id",
        vk_access_token="test-vk-token",
        vk_group_id="test-vk-group",
        max_bot_token="test-max-token",
        max_chat_id="test-max-chat",
        jaccard_threshold=0.55,
        embedding_similarity_threshold=0.75,
        dedup_window_days_stage1=7,
        dedup_window_days_stage2=5,
        cleanup_retention_days=90,
        pipeline_interval_hours=3,
        max_articles_per_run=20,
        post_length_min=700,
        post_length_max=3000,
        post_total_max_length=1000,
        embedding_model="text-embedding-004",
        default_template_id="news_brief",
        template_pool=[
            "news_brief", "deep_dive", "quick_take", "expert_opinion",
            "case_study", "trend_analysis", "tool_review", "research_summary",
            "industry_news", "tutorial_style"
        ],
    )

# ============================================================================
# Repository Fixtures
# ============================================================================

@pytest.fixture
def source_repo(test_session: AsyncSession) -> SqlAlchemySourceRepository:
    """Source repository fixture."""
    return SqlAlchemySourceRepository(test_session)


@pytest.fixture
def channel_repo(test_session: AsyncSession) -> SqlAlchemyChannelRepository:
    """Channel repository fixture."""
    return SqlAlchemyChannelRepository(test_session)


@pytest.fixture
def llm_model_repo(test_session: AsyncSession) -> SqlAlchemyLLMModelRepository:
    """LLM model repository fixture."""
    return SqlAlchemyLLMModelRepository(test_session)


@pytest.fixture
def setting_repo(test_session: AsyncSession) -> SqlAlchemySettingRepository:
    """Setting repository fixture."""
    return SqlAlchemySettingRepository(test_session)


@pytest.fixture
def post_repo(test_session: AsyncSession) -> SqlAlchemyPostRepository:
    """Post repository fixture."""
    return SqlAlchemyPostRepository(test_session)


@pytest.fixture
def user_repo(test_session: AsyncSession) -> SqlAlchemyUserRepository:
    """User repository fixture."""
    return SqlAlchemyUserRepository(test_session)


@pytest.fixture
def log_repo(test_session: AsyncSession) -> SqlAlchemyLogRepository:
    """Log repository fixture."""
    return SqlAlchemyLogRepository(test_session)


# ============================================================================
# Mock Client Fixtures
# ============================================================================

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client."""
    from infrastructure.clients.gemini_client import MockGeminiClient
    return MockGeminiClient()


@pytest.fixture
def mock_jina_client():
    """Mock Jina client."""
    from infrastructure.clients.jina_client import MockJinaClient
    return MockJinaClient()


@pytest.fixture
def mock_telegram_client():
    """Mock Telegram client."""
    from infrastructure.clients.telegram_client import MockTelegramClient
    return MockTelegramClient()


@pytest.fixture
def mock_vk_client():
    """Mock VK client."""
    from infrastructure.clients.vk_client import MockVKClient
    return MockVKClient()


@pytest.fixture
def mock_max_client():
    """Mock Max client."""
    from infrastructure.clients.max_client import MockMaxClient
    return MockMaxClient()

# ============================================================================
# Repository Fixtures
# ============================================================================

@pytest.fixture
def source_repo(test_session: AsyncSession) -> SqlAlchemySourceRepository:
    """Source repository fixture."""
    return SqlAlchemySourceRepository(test_session)


@pytest.fixture
def channel_repo(test_session: AsyncSession) -> SqlAlchemyChannelRepository:
    """Channel repository fixture."""
    return SqlAlchemyChannelRepository(test_session)


@pytest.fixture
def llm_model_repo(test_session: AsyncSession) -> SqlAlchemyLLMModelRepository:
    """LLM model repository fixture."""
    return SqlAlchemyLLMModelRepository(test_session)


@pytest.fixture
def setting_repo(test_session: AsyncSession) -> SqlAlchemySettingRepository:
    """Setting repository fixture."""
    return SqlAlchemySettingRepository(test_session)


@pytest.fixture
def post_repo(test_session: AsyncSession) -> SqlAlchemyPostRepository:
    """Post repository fixture."""
    return SqlAlchemyPostRepository(test_session)


@pytest.fixture
def user_repo(test_session: AsyncSession) -> SqlAlchemyUserRepository:
    """User repository fixture."""
    return SqlAlchemyUserRepository(test_session)


@pytest.fixture
def log_repo(test_session: AsyncSession) -> SqlAlchemyLogRepository:
    """Log repository fixture."""
    return SqlAlchemyLogRepository(test_session)


# ============================================================================
# Mock Client Fixtures
# ============================================================================

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client."""
    from infrastructure.clients.gemini_client import MockGeminiClient
    return MockGeminiClient()


@pytest.fixture
def mock_jina_client():
    """Mock Jina client."""
    from infrastructure.clients.jina_client import MockJinaClient
    return MockJinaClient()


@pytest.fixture
def mock_telegram_client():
    """Mock Telegram client."""
    from infrastructure.clients.telegram_client import MockTelegramClient
    return MockTelegramClient()


@pytest.fixture
def mock_vk_client():
    """Mock VK client."""
    from infrastructure.clients.vk_client import MockVKClient
    return MockVKClient()


@pytest.fixture
def mock_max_client():
    """Mock Max client."""
    from infrastructure.clients.max_client import MockMaxClient
    return MockMaxClient()


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_rss_feed() -> str:
    """Sample RSS feed XML for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test Tech News</title>
        <link>https://example.com</link>
        <description>Test tech news feed</description>
        <item>
            <title>AI Breakthrough in Machine Learning</title>
            <link>https://example.com/article/1</link>
            <description>Scientists achieve major breakthrough in ML</description>
            <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
            <guid>https://example.com/article/1</guid>
            <enclosure url="https://example.com/image1.jpg" type="image/jpeg"/>
        </item>
        <item>
            <title>New Python Release 3.13</title>
            <link>https://example.com/article/2</link>
            <description>Python 3.13 brings performance improvements</description>
            <pubDate>Mon, 01 Jan 2024 13:00:00 GMT</pubDate>
            <guid>https://example.com/article/2</guid>
        </item>
        <item>
            <title>Quantum Computing Advances</title>
            <link>https://example.com/article/3</link>
            <description>Researchers make progress in quantum computing</description>
            <pubDate>Mon, 01 Jan 2024 14:00:00 GMT</pubDate>
            <guid>https://example.com/article/3</guid>
        </item>
    </channel>
</rss>"""


@pytest.fixture
def sample_articles() -> list:
    """Create sample Article entities for testing."""
    from domain.entities.article import Article
    from domain.value_objects.url import URL
    from datetime import datetime, timezone
    
    articles = []
    for i in range(5):
        article = Article(
            id=i + 1,
            title=fake.sentence(nb_words=6),
            url=URL.from_string(f"https://example.com/article/{i+1}"),
            summary=fake.paragraph(nb_sentences=2),
            published_at=datetime.now(timezone.utc),
            source_id=1,
            image_url=f"https://example.com/image{i+1}.jpg" if i % 2 == 0 else None,
        )
        articles.append(article)
    return articles


@pytest.fixture
def sample_posts() -> list:
    """Create sample Post entities for testing."""
    from domain.entities.post import Post
    from domain.value_objects.embedding import Embedding
    from domain.value_objects.url import URL
    from datetime import datetime, timezone
    import random
    
    posts = []
    for i in range(5):
        # Create deterministic embedding for testing
        vector = [random.uniform(-1, 1) for _ in range(768)]
        # Normalize
        norm = sum(v*v for v in vector) ** 0.5
        vector = [v/norm for v in vector]
        
        post = Post(
            id=i + 1,
            title=fake.sentence(nb_words=6),
            summary=fake.paragraph(nb_sentences=2),
            content=fake.paragraph(nb_sentences=5),
            clean_url=f"https://example.com/post/{i+1}",
            embedding=Embedding.from_list(vector),
            image_url=f"https://example.com/image{i+1}.jpg" if i % 2 == 0 else None,
            is_duplicate=False,
            source_id=1,
            channel_id=1,
            llm_model_id=1,
            template_id="news_brief",
            created_at=datetime.now(timezone.utc),
        )
        posts.append(post)
    return posts


@pytest.fixture
def duplicate_post_pair() -> tuple:
    """Create a pair of posts with high embedding similarity (duplicates)."""
    from domain.entities.post import Post
    from domain.value_objects.embedding import Embedding
    from datetime import datetime, timezone
    
    # Create base embedding
    base_vector = [0.1] * 768
    base_vector[0] = 0.9
    base_norm = sum(v*v for v in base_vector) ** 0.5
    base_vector = [v/base_norm for v in base_vector]
    
    # Create similar embedding (cosine similarity ~0.95)
    similar_vector = base_vector.copy()
    similar_vector[1] = 0.2
    similar_norm = sum(v*v for v in similar_vector) ** 0.5
    similar_vector = [v/similar_norm for v in similar_vector]
    
    post1 = Post(
        id=1,
        title="Original Article Title",
        summary="Original summary",
        content="Original content",
        clean_url="https://example.com/original",
        embedding=Embedding.from_list(base_vector),
        image_url="https://example.com/image1.jpg",
        is_duplicate=False,
        source_id=1,
        channel_id=1,
        llm_model_id=1,
        template_id="news_brief",
        created_at=datetime.now(timezone.utc),
    )
    
    post2 = Post(
        id=2,
        title="Similar Article Title",
        summary="Similar summary",
        content="Similar content",
        clean_url="https://example.com/similar",
        embedding=Embedding.from_list(similar_vector),
        image_url="https://example.com/image2.jpg",
        is_duplicate=False,
        source_id=1,
        channel_id=1,
        llm_model_id=1,
        template_id="news_brief",
        created_at=datetime.now(timezone.utc),
    )
    
    return post1, post2


# ============================================================================
# Pipeline Context Fixtures
# ============================================================================

@pytest.fixture
def pipeline_context() -> Any:
    """Create a fresh PipelineContext for testing."""
    from application.dto.pipeline_context import PipelineContext
    return PipelineContext()


@pytest.fixture
def populated_pipeline_context(sample_articles) -> Any:
    """Create PipelineContext with sample articles."""
    from application.dto.pipeline_context import PipelineContext
    context = PipelineContext()
    context.raw_articles = sample_articles
    context.deduplicated_articles = sample_articles
    return context


# ============================================================================
# Client Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_gemini_client() -> Any:
    """Create a mock Gemini client."""
    from infrastructure.clients.gemini_client import MockGeminiClient
    return MockGeminiClient()


@pytest.fixture
def mock_jina_client() -> Any:
    """Create a mock Jina client."""
    from infrastructure.clients.jina_client import MockJinaClient
    return MockJinaClient()


@pytest.fixture
def mock_telegram_client() -> Any:
    """Create a mock Telegram client."""
    from infrastructure.clients.telegram_client import MockTelegramClient
    return MockTelegramClient()


@pytest.fixture
def mock_vk_client() -> Any:
    """Create a mock VK client."""
    from infrastructure.clients.vk_client import MockVKClient
    return MockVKClient()


@pytest.fixture
def mock_max_client() -> Any:
    """Create a mock Max client."""
    from infrastructure.clients.max_client import MockMaxClient
    return MockMaxClient()


# ============================================================================
# Service Fixtures
# ============================================================================

@pytest.fixture
def llm_service() -> Any:
    """Create LLMService with mock provider."""
    from application.services.llm_service import LLMService, MockLLMProvider
    return LLMService(provider=MockLLMProvider())


@pytest.fixture
def embedding_service(mock_gemini_client) -> Any:
    """Create EmbeddingService with mock client."""
    from application.services.embedding_service import EmbeddingService
    return EmbeddingService(client=mock_gemini_client)


@pytest.fixture
def image_service(mock_jina_client) -> Any:
    """Create ImageService with mock client."""
    from application.services.image_service import ImageService
    return ImageService(client=mock_jina_client)


@pytest.fixture
def publisher_service(test_settings, mock_telegram_client, mock_vk_client, mock_max_client) -> Any:
    """Create PublisherService with test settings and mock clients."""
    from application.services.publisher_service import PublisherService
    from infrastructure.config import Settings
    # Patch get_settings in both the config module AND the publisher_service module
    # because publisher_service imports get_settings directly
    import infrastructure.config as config_module
    import application.services.publisher_service as publisher_module
    original_get_settings = config_module.get_settings
    # test_settings is already a Settings object (fixture returns it)
    # Clear the lru_cache on the original function
    original_get_settings.cache_clear()
    # Create a new cached function
    from functools import lru_cache
    @lru_cache
    def patched_get_settings():
        result = test_settings  # test_settings is already a Settings object
        print(f"DEBUG patched_get_settings: returning settings with app_env={result.app_env}")
        configs = result.get_channel_configs()
        print(f"DEBUG patched_get_settings: configs = {configs}")
        return result
    # Patch in both modules
    config_module.get_settings = patched_get_settings
    publisher_module.get_settings = patched_get_settings
    try:
        print(f"DEBUG: Creating PublisherService with clients: telegram={type(mock_telegram_client)}, vk={type(mock_vk_client)}, max={type(mock_max_client)}")
        print(f"DEBUG: get_settings in config_module: {config_module.get_settings}")
        print(f"DEBUG: get_settings in publisher_module: {publisher_module.get_settings}")
        service = PublisherService(
            telegram_client=mock_telegram_client,
            vk_client=mock_vk_client,
            max_client=mock_max_client,
        )
        print(f"DEBUG: Created service with publishers: {list(service._publishers.keys())}")
        return service
    finally:
        # Restore original function
        config_module.get_settings = original_get_settings
        publisher_module.get_settings = original_get_settings
        original_get_settings.cache_clear()


@pytest.fixture
def deduplication_service(post_repo) -> Any:
    """Create DeduplicationService."""
    from application.services.deduplication_service import DeduplicationService
    return DeduplicationService(post_repo=post_repo)


@pytest.fixture
def notification_service() -> Any:
    """Create NotificationService with mock telegram client."""
    from application.services.notification_service import NotificationService
    from infrastructure.clients.telegram_client import MockTelegramClient
    return NotificationService(client=MockTelegramClient())


# ============================================================================
# Pipeline Step Fixtures
# ============================================================================

@pytest.fixture
def fetch_rss_step() -> Any:
    """Create FetchRSSStep."""
    from application.pipeline.steps.fetch_rss import FetchRSSStep
    return FetchRSSStep()


@pytest.fixture
def deduplicate_step(deduplication_service) -> Any:
    """Create DeduplicateStep."""
    from application.pipeline.steps.deduplicate import DeduplicateStep
    return DeduplicateStep(dedup_service=deduplication_service)


@pytest.fixture
def select_top_step(llm_service) -> Any:
    """Create SelectTopStep."""
    from application.pipeline.steps.select_top import SelectTopStep
    return SelectTopStep(llm_service=llm_service, max_articles=3)


@pytest.fixture
def extract_content_step(image_service) -> Any:
    """Create ExtractContentStep."""
    from application.pipeline.steps.extract_content import ExtractContentStep
    return ExtractContentStep(image_service=image_service)


@pytest.fixture
def generate_post_step(llm_service) -> Any:
    """Create GeneratePostStep."""
    from application.pipeline.steps.generate_post import GeneratePostStep
    return GeneratePostStep(llm_service=llm_service)


@pytest.fixture
def compute_embedding_step(embedding_service) -> Any:
    """Create ComputeEmbeddingStep."""
    from application.pipeline.steps.compute_embedding import ComputeEmbeddingStep
    return ComputeEmbeddingStep(embedding_service=embedding_service)


@pytest.fixture
def check_embedding_duplicate_step(deduplication_service) -> Any:
    """Create CheckEmbeddingDuplicateStep."""
    from application.pipeline.steps.check_embedding_duplicate import CheckEmbeddingDuplicateStep
    return CheckEmbeddingDuplicateStep(dedup_service=deduplication_service)


@pytest.fixture
def publish_step(publisher_service) -> Any:
    """Create PublishStep."""
    from application.pipeline.steps.publish import PublishStep
    return PublishStep(publisher_service=publisher_service)


# ============================================================================
# Full Pipeline Fixture
# ============================================================================

@pytest.fixture
def full_pipeline(
    fetch_rss_step,
    deduplicate_step,
    select_top_step,
    extract_content_step,
    generate_post_step,
    compute_embedding_step,
    check_embedding_duplicate_step,
    publish_step,
    notification_service,
) -> Any:
    """Create a complete Pipeline with all steps."""
    from application.pipeline.pipeline import Pipeline
    return Pipeline(
        steps=[
            fetch_rss_step,
            deduplicate_step,
            select_top_step,
            extract_content_step,
            generate_post_step,
            compute_embedding_step,
            check_embedding_duplicate_step,
            publish_step,
        ],
        notification_service=notification_service,
    )
