"""Pipeline Context DTO.

Shared data passed between pipeline steps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from domain.entities.article import Article
from domain.entities.post import Post
from domain.value_objects.embedding import Embedding


@dataclass
class PipelineContext:
    """Context passed through pipeline steps."""

    # Input
    rss_sources: List[Any] = field(default_factory=list)  # RssSource entities
    settings: Dict[str, Any] = field(default_factory=dict)

    # Step 1: Fetch RSS
    raw_articles: List[Article] = field(default_factory=list)

    # Step 2: Deduplicate (Stage 1)
    deduplicated_articles: List[Article] = field(default_factory=list)

    # Step 3: Select Top
    selected_article_indices: List[int] = field(default_factory=list)
    selected_articles: List[Article] = field(default_factory=list)

    # Step 4: Extract Content
    extracted_articles: List[Dict[str, Any]] = field(default_factory=list)

    # Step 5: Generate Post
    generated_posts: List[Dict[str, Any]] = field(default_factory=list)

    # Step 6: Compute Embedding
    post_embeddings: List[Embedding] = field(default_factory=list)

    # Step 7: Deduplicate (Stage 2)
    final_posts: List[Post] = field(default_factory=list)
    duplicate_posts: List[Post] = field(default_factory=list)

    # Step 8: Publish
    published_results: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def get_articles_for_selection(self) -> List[Dict[str, Any]]:
        """Get articles formatted for LLM selection."""
        return [
            {
                "id": i + 1,
                "title": a.title,
                "summary": a.summary,
                "url": str(a.url),
            }
            for i, a in enumerate(self.deduplicated_articles)
        ]

    def get_recent_titles(self, limit: int = 10) -> List[str]:
        """Get recent published titles for duplicate avoidance."""
        # This would typically come from post_repo
        return []

    def add_error(self, step: str, error: str) -> None:
        """Add error to context."""
        self.errors.append(f"[{step}] {error}")

    def add_metric(self, key: str, value: Any) -> None:
        """Add metric to context."""
        self.metrics[key] = value
