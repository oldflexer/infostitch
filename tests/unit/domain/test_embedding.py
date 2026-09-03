"""Unit tests for Embedding value object."""
from __future__ import annotations

import pytest
import math

from domain.value_objects.embedding import Embedding


class TestEmbedding:
    """Tests for Embedding value object."""

    def test_from_list(self):
        """Test creating embedding from list of floats."""
        vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        embedding = Embedding.from_list(vector)

        assert embedding.vector == vector
        assert len(embedding.vector) == 5

    def test_from_list_does_not_normalize(self):
        """Test that from_list does NOT normalize the vector (stores as-is)."""
        vector = [3.0, 4.0]  # Length 5
        embedding = Embedding.from_list(vector)

        # Should store as-is, not normalized
        assert embedding.vector == [3.0, 4.0]
        norm = math.sqrt(sum(v * v for v in embedding.vector))
        assert abs(norm - 5.0) < 1e-10

    def test_cosine_similarity_identical(self):
        """Test cosine similarity of identical vectors."""
        vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        emb1 = Embedding.from_list(vector)
        emb2 = Embedding.from_list(vector)

        similarity = emb1.cosine_similarity(emb2)
        assert abs(similarity - 1.0) < 1e-10

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity of orthogonal vectors."""
        emb1 = Embedding.from_list([1.0, 0.0, 0.0])
        emb2 = Embedding.from_list([0.0, 1.0, 0.0])

        similarity = emb1.cosine_similarity(emb2)
        assert abs(similarity - 0.0) < 1e-10

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity of opposite vectors."""
        emb1 = Embedding.from_list([1.0, 0.0, 0.0])
        emb2 = Embedding.from_list([-1.0, 0.0, 0.0])

        similarity = emb1.cosine_similarity(emb2)
        assert abs(similarity - (-1.0)) < 1e-10

    def test_cosine_distance(self):
        """Test cosine distance (1 - cosine_similarity)."""
        emb1 = Embedding.from_list([1.0, 0.0, 0.0])
        emb2 = Embedding.from_list([0.0, 1.0, 0.0])

        distance = emb1.cosine_distance(emb2)
        assert abs(distance - 1.0) < 1e-10

    def test_is_similar_to(self):
        """Test is_similar_to with threshold."""
        emb1 = Embedding.from_list([1.0, 0.0, 0.0])
        emb2 = Embedding.from_list([1.0, 0.0, 0.0])
        emb3 = Embedding.from_list([0.0, 1.0, 0.0])

        assert emb1.is_similar_to(emb2, threshold=0.75) is True
        assert emb1.is_similar_to(emb3, threshold=0.75) is False

    def test_to_bytes(self):
        """Test serialization to bytes."""
        vector = [0.1, 0.2, 0.3]
        embedding = Embedding.from_list(vector)

        data = embedding.to_bytes()
        assert isinstance(data, bytes)

        # Should be able to deserialize
        restored = Embedding.from_bytes(data)
        # Allow small floating point differences
        for a, b in zip(restored.vector, embedding.vector):
            assert abs(a - b) < 1e-6

    def test_dimension_mismatch_raises(self):
        """Test that cosine similarity raises on dimension mismatch."""
        emb1 = Embedding.from_list([1.0, 0.0])
        emb2 = Embedding.from_list([1.0, 0.0, 0.0])

        with pytest.raises(ValueError, match="Dimension mismatch"):
            emb1.cosine_similarity(emb2)

    def test_empty_vector_raises(self):
        """Test that empty vector raises ValueError."""
        with pytest.raises(ValueError, match="Embedding vector cannot be empty"):
            Embedding.from_list([])

    def test_non_numeric_raises(self):
        """Test that non-numeric values raise ValueError."""
        with pytest.raises(ValueError, match="All embedding values must be numeric"):
            Embedding.from_list([1.0, "invalid", 3.0])

    def test_dimension_property(self):
        """Test dimension property."""
        embedding = Embedding.from_list([1.0, 2.0, 3.0, 4.0])
        assert embedding.dimension == 4

    def test_len(self):
        """Test len() returns dimension."""
        embedding = Embedding.from_list([1.0, 2.0, 3.0])
        assert len(embedding) == 3

    def test_getitem(self):
        """Test indexing."""
        embedding = Embedding.from_list([1.0, 2.0, 3.0])
        assert embedding[0] == 1.0
        assert embedding[1] == 2.0
        assert embedding[2] == 3.0

    def test_iteration(self):
        """Test iteration."""
        embedding = Embedding.from_list([1.0, 2.0, 3.0])
        values = list(embedding)
        assert values == [1.0, 2.0, 3.0]
