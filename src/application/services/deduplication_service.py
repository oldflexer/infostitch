"""Deduplication Service.

Implements multi-stage deduplication:
1. URL-based (exact match)
2. Jaccard similarity on titles
3. Semantic similarity via embeddings
"""
from __future__ import annotations

from typing import List, Optional, Set

from domain.value_objects.embedding import Embedding
from domain.value_objects.url import URL
from domain.repositories.post_repo import PostRepository
from domain.entities.article import Article
from domain.entities.article import Article


class DeduplicationService:
    """Service for article deduplication."""

    def __init__(
        self,
        post_repo: PostRepository,
        jaccard_threshold: float = 0.55,
        embedding_threshold: float = 0.75,
        stage1_window_days: int = 7,
        stage2_window_days: int = 5,
    ):
        self._post_repo = post_repo
        self._jaccard_threshold = jaccard_threshold
        self._embedding_threshold = embedding_threshold
        self._stage1_window_days = stage1_window_days
        self._stage2_window_days = stage2_window_days

    @staticmethod
    def jaccard_similarity(text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        # Tokenize into words (lowercase, alphanumeric)
        import re
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def is_duplicate_by_url(self, url: str) -> bool:
        """Check if URL already published (Stage 0)."""
        clean_url = URL.from_string(url).clean_for_dedup()
        return self._post_repo.exists_by_url(clean_url)

    def is_duplicate_by_jaccard(
        self,
        title: str,
        recent_titles: List[str],
    ) -> bool:
        """Check if title is similar to recent titles using Jaccard (Stage 1)."""
        for recent_title in recent_titles:
            similarity = self.jaccard_similarity(title, recent_title)
            if similarity >= self._jaccard_threshold:
                return True
        return False

    async def is_duplicate_by_embedding(
        self,
        embedding: Embedding,
    ) -> Optional[dict]:
        """Check semantic duplicate via embedding similarity (Stage 2).

        Returns:
            Dict with matched post info if duplicate, None otherwise
        """
        similar_post = await self._post_repo.find_similar(
            embedding=embedding,
            threshold=self._embedding_threshold,
            days=self._stage2_window_days,
        )
        if similar_post:
            return {
                "post_id": similar_post.id,
                "title": similar_post.title,
                "similarity": embedding.cosine_similarity(similar_post.embedding),
            }
        return None

    async def filter_by_url(self, articles: List[Article]) -> List[Article]:
        """Filter articles by URL deduplication."""
        filtered = []
        for a in articles:
            if not await self.is_duplicate_by_url(str(a.url)):
                filtered.append(a)
        return filtered

    def filter_by_jaccard(
        self,
        articles: List[Article],
        recent_titles: List[str],
    ) -> List[Article]:
        """Filter articles by Jaccard similarity."""
        return [
            a for a in articles
            if not self.is_duplicate_by_jaccard(a.title, recent_titles)
        ]

    async def filter_by_embedding(
        self,
        articles: List[Article],
        embeddings: List[Embedding],
    ) -> List[Article]:
        """Filter articles by semantic similarity."""
        filtered = []
        for article, embedding in zip(articles, embeddings):
            duplicate = await self.is_duplicate_by_embedding(embedding)
            if not duplicate:
                filtered.append(article)
        return filtered