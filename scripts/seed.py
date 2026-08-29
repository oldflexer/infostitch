#!/usr/bin/env python3
"""Database seeding script.

Run after migrations to populate initial data.
"""
import asyncio
import json
from passlib.hash import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config import get_settings, DEFAULT_SETTINGS
from infrastructure.db.session import get_db_manager, init_db
from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository
from infrastructure.db.repositories.channel_repo import SqlAlchemyChannelRepository
from infrastructure.db.repositories.llm_model_repo import SqlAlchemyLLMModelRepository
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository
from infrastructure.db.repositories.user_repo import SqlAlchemyUserRepository
from domain.entities.rss_source import RssSource
from domain.entities.channel import Channel
from domain.entities.llm_model import LLMModel


async def seed_settings(session: AsyncSession) -> None:
    """Seed default settings."""
    repo = SqlAlchemySettingRepository(session)
    await repo.initialize_defaults(DEFAULT_SETTINGS)
    print("✓ Settings seeded")


async def seed_admin_user(session: AsyncSession) -> None:
    """Seed default admin user."""
    repo = SqlAlchemyUserRepository(session)
    settings = get_settings()

    existing = await repo.get_by_username(settings.admin_username)
    if not existing:
        await repo.create(
            username=settings.admin_username,
            password=settings.admin_password,
            role="admin",
        )
        print(f"✓ Admin user created: {settings.admin_username}")
    else:
        print("✓ Admin user already exists")


async def seed_rss_sources(session: AsyncSession) -> None:
    """Seed example RSS sources."""
    repo = SqlAlchemySourceRepository(session)

    sources = [
        "https://feeds.feedburner.com/TechCrunch/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
        "https://arstechnica.com/feed/",
        "https://www.engadget.com/rss.xml",
        "https://www.technologyreview.com/feed/",
        "https://www.zdnet.com/news/rss.xml",
        "https://www.cnet.com/rss/news/",
    ]

    for url in sources:
        existing = await repo.get_by_url(url)
        if not existing:
            source = RssSource(url=url, enabled=True)
            await repo.add(source)
            print(f"✓ RSS source added: {url}")
        else:
            print(f"✓ RSS source exists: {url}")


async def seed_channels(session: AsyncSession) -> None:
    """Seed example channels from environment."""
    repo = SqlAlchemyChannelRepository(session)
    settings = get_settings()

    channel_configs = settings.get_channel_configs()

    for ch_type, config in channel_configs.items():
        name = f"{ch_type.capitalize()} Channel"
        existing = await repo.get_by_name(name)
        if not existing:
            channel = Channel(name=name, type=ch_type, enabled=True, config=config)
            await repo.add(channel)
            print(f"✓ Channel added: {name} ({ch_type})")
        else:
            print(f"✓ Channel exists: {name}")


async def seed_llm_models(session: AsyncSession) -> None:
    """Seed default LLM models."""
    repo = SqlAlchemyLLMModelRepository(session)
    settings = get_settings()

    models = [
        LLMModel(
            name="gemini-1.5-flash",
            provider="gemini",
            model_id="gemini-1.5-flash-latest",
            api_key_ref="GEMINI_API_KEY",
        ),
        LLMModel(
            name="gemini-1.5-pro",
            provider="gemini",
            model_id="gemini-1.5-pro-latest",
            api_key_ref="GEMINI_API_KEY",
        ),
    ]

    for model in models:
        existing = await repo.get_by_name(model.name)
        if not existing:
            await repo.add(model)
            print(f"✓ LLM model added: {model.name}")
        else:
            print(f"✓ LLM model exists: {model.name}")


async def main() -> None:
    """Main seeding function."""
    print("Starting database seeding...")

    # Initialize database
    await init_db()

    # Get session
    db_manager = get_db_manager()
    async with db_manager.session() as session:
        await seed_settings(session)
        await seed_admin_user(session)
        await seed_rss_sources(session)
        await seed_channels(session)
        await seed_llm_models(session)

    await db_manager.close()
    print("✓ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())