#!/usr/bin/env python3
"""CLI Entry Point for InfoStitch Pipeline.

Usage:
    python -m src.presentation.cli.run          # Run pipeline once
    python -m src.presentation.cli.run --help   # Show help
"""
from __future__ import annotations
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository
from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository
from infrastructure.db.session import get_db_manager
from application.services.notification_service import NotificationService
from application.services.publisher_service import PublisherService
from application.services.deduplication_service import DeduplicationService
from application.services.image_service import ImageService
from application.services.embedding_service import EmbeddingService
from application.services.llm_service import LLMService
from application.dto.pipeline_context import PipelineContext
from application.pipeline.steps.publish import PublishStep
from application.pipeline.steps.check_embedding_duplicate import CheckEmbeddingDuplicateStep
from application.pipeline.steps.compute_embedding import ComputeEmbeddingStep
from application.pipeline.steps.generate_post import GeneratePostStep
from application.pipeline.steps.extract_content import ExtractContentStep
from application.pipeline.steps.select_top import SelectTopStep
from application.pipeline.steps.deduplicate import DeduplicateStep
from application.pipeline.steps.fetch_rss import FetchRSSStep
from application.pipeline.pipeline import Pipeline
from infrastructure.logging.metrics import init_metrics
from infrastructure.db.session import get_db_manager, init_db, close_db
from infrastructure.config import get_settings

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# Pipeline imports


async def run_pipeline(dry_run: bool = False) -> int:
    """Run the news aggregation pipeline once."""
    print("🚀 Starting InfoStitch pipeline...")

    settings = get_settings()
    print(f"Environment: {settings.app_env}")
    print(f"Database: {settings.database_url}")

    if dry_run:
        print("🔍 DRY RUN MODE - No publishing")

    # Initialize metrics
    init_metrics()

    # Initialize database
    await init_db()

    # Get database session
    db_manager = get_db_manager()
    async with db_manager.session() as session:
        # Initialize repositories
        source_repo = SqlAlchemySourceRepository(session)
        post_repo = SqlAlchemyPostRepository(session)
        setting_repo = SqlAlchemySettingRepository(session)

        # Load settings from DB
        db_settings = await setting_repo.get_all()

        # Initialize services
        llm_service = LLMService()
        embedding_service = EmbeddingService()
        image_service = ImageService()
        dedup_service = DeduplicationService(
            post_repo=post_repo,
            jaccard_threshold=settings.jaccard_threshold,
            embedding_threshold=settings.embedding_similarity_threshold,
            stage1_window_days=settings.dedup_window_days_stage1,
            stage2_window_days=settings.dedup_window_days_stage2,
        )
        publisher_service = PublisherService()
        notification_service = NotificationService()

        # Get enabled RSS sources
        rss_sources = await source_repo.get_enabled()

        # Build pipeline context
        context = PipelineContext(
            rss_sources=rss_sources,
            settings=db_settings,
        )

        # Build pipeline
        pipeline = Pipeline(steps=[
            FetchRSSStep(),
            DeduplicateStep(dedup_service),
            SelectTopStep(
                LLMService(), max_articles=settings.max_articles_per_run),
            ExtractContentStep(ImageService()),
            GeneratePostStep(LLMService()),
            ComputeEmbeddingStep(EmbeddingService()),
            CheckEmbeddingDuplicateStep(dedup_service),
            PublishStep(PublisherService()),
        ], notification_service=notification_service)

        try:
            print("📡 Running pipeline...")
            context = await pipeline.run(context)

            # Print results
            print(f"\n📊 Pipeline Results:")
            print(f"  Fetched: {context.metrics.get('total_fetched', 0)}")
            print(
                f"  After URL dedup: {
                    context.metrics.get(
                        'after_url_dedup',
                        0)}")
            print(
                f"  After Jaccard dedup: {
                    context.metrics.get(
                        'after_jaccard_dedup',
                        0)}")
            print(f"  Selected: {context.metrics.get('selected_count', 0)}")
            print(f"  Extracted: {context.metrics.get('extracted_count', 0)}")
            print(f"  Generated: {context.metrics.get('generated_count', 0)}")
            print(
                f"  Embeddings: {
                    context.metrics.get(
                        'embeddings_computed',
                        0)}")
            print(f"  Final posts: {context.metrics.get('final_posts', 0)}")
            print(f"  Duplicates: {context.metrics.get('duplicate_posts', 0)}")
            print(f"  Published: {context.metrics.get('published_count', 0)}")

            if context.errors:
                print(f"\n⚠️  Errors ({len(context.errors)}):")
                for error in context.errors:
                    print(f"  - {error}")

            if dry_run:
                print("\n🔍 DRY RUN - No posts were actually published")

        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            return 1
        finally:
            # Close services
            await llm_service.close()
            await embedding_service.close()
            await image_service.close()
            await publisher_service.close()
            await notification_service.close()

    await close_db()
    return 0


async def clear_old_data(days: int = 90) -> int:
    """Clear old published posts."""
    print(f"🗑️  Clearing posts older than {days} days...")

    await init_db()
    db_manager = get_db_manager()

    async with db_manager.session() as session:
        from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
        repo = SqlAlchemyPostRepository(session)
        deleted = await repo.cleanup_old(days)
        print(f"✓ Deleted {deleted} old posts")

    await close_db()
    return 0


async def show_config() -> int:
    """Show current configuration."""
    settings = get_settings()

    print("📋 Current Configuration:")
    print(f"  Environment: {settings.app_env}")
    print(f"  Database: {settings.database_url}")
    print(f"  Pipeline interval: {settings.pipeline_interval_hours}h")
    print(f"  Max articles per run: {settings.max_articles_per_run}")
    print(f"  Jaccard threshold: {settings.jaccard_threshold}")
    print(f"  Embedding threshold: {settings.embedding_similarity_threshold}")
    print(
        f"  Post length: {settings.post_length_min}-{settings.post_length_max}")
    print(f"  Cleanup retention: {settings.cleanup_retention_days} days")

    # Show DB settings
    db_manager = get_db_manager()
    async with db_manager.session() as session:
        from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository
        repo = SqlAlchemySettingRepository(session)
        db_settings = await repo.get_all()
        if db_settings:
            print("\n  Database settings:")
            for key, value in sorted(db_settings.items()):
                print(f"    {key}: {value}")

    await close_db()
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="infostitch",
        description="News Aggregator & Publisher System",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Run pipeline
    run_parser = subparsers.add_parser("run", help="Run pipeline once")
    run_parser.add_argument(
        "--dry-run", action="store_true", help="Run without publishing"
    )

    # Clear old data
    clear_parser = subparsers.add_parser("clear", help="Clear old data")
    clear_parser.add_argument(
        "--days", type=int, default=90, help="Days to retain (default: 90)"
    )

    # Show config
    config_parser = subparsers.add_parser("config", help="Show configuration")

    # Init DB
    init_parser = subparsers.add_parser("init-db", help="Initialize database")

    # Seed DB
    seed_parser = subparsers.add_parser(
        "seed", help="Seed database with defaults")

    args = parser.parse_args()

    # Route to appropriate handler
    if args.command == "run":
        return asyncio.run(run_pipeline())
    elif args.command == "clear":
        return asyncio.run(clear_old_data(args.days))
    elif args.command == "config":
        return asyncio.run(show_config())
    elif args.command == "init-db":
        print("🔧 Initializing database...")
        asyncio.run(init_db())
        print("✓ Database initialized")
        return 0
    elif args.command == "seed":
        print("🌱 Seeding database...")
        from scripts.seed import main as seed_main
        asyncio.run(seed_main())
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
