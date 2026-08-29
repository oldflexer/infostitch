#!/usr/bin/env python3
"""CLI Entry Point for InfoStitch Pipeline.

Usage:
    python -m src.presentation.cli.run          # Run pipeline once
    python -m src.presentation.cli.run --help   # Show help
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from infrastructure.config import get_settings
from infrastructure.db.session import get_db_manager, init_db, close_db


async def run_pipeline() -> int:
    """Run the news aggregation pipeline once."""
    print("🚀 Starting InfoStitch pipeline...")

    settings = get_settings()
    print(f"Environment: {settings.app_env}")
    print(f"Database: {settings.database_url}")

    # Initialize database
    await init_db()

    # TODO: Implement actual pipeline logic
    # This is a placeholder for Iteration 1
    print("⚠️  Pipeline not yet implemented (Iteration 1)")
    print("   - Fetch RSS feeds")
    print("   - Deduplicate articles")
    print("   - Select top candidates")
    print("   - Extract content")
    print("   - Generate posts")
    print("   - Compute embeddings")
    print("   - Check semantic duplicates")
    print("   - Publish to channels")

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
    print(f"  Post length: {settings.post_length_min}-{settings.post_length_max}")
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
    seed_parser = subparsers.add_parser("seed", help="Seed database with defaults")

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