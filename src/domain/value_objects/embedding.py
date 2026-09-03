"""Embedding Value Object.

Represents a vector embedding with utility methods for similarity computation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence


@dataclass(frozen=True, slots=True)
class Embedding:
    """Immutable value object representing a vector embedding."""

    vector: List[float]

    def __post_init__(self) -> None:
        """Validate embedding after initialization."""
        if not self.vector:
            raise ValueError("Embedding vector cannot be empty")

        if not all(isinstance(x, (int, float)) for x in self.vector):
            raise ValueError("All embedding values must be numeric")

        # Ensure all values are floats
        object.__setattr__(self, "vector", [float(x) for x in self.vector])

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return len(self.vector)

    def cosine_similarity(self, other: Embedding) -> float:
        """Compute cosine similarity with another embedding.

        Returns value in [-1, 1], where 1 = identical, 0 = orthogonal, -1 = opposite.
        """
        if self.dimension != other.dimension:
            raise ValueError(
                f"Dimension mismatch: {self.dimension} vs {other.dimension}"
            )

        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        norm_a = math.sqrt(sum(a * a for a in self.vector))
        norm_b = math.sqrt(sum(b * b for b in other.vector))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def cosine_distance(self, other: Embedding) -> float:
        """Compute cosine distance (1 - cosine_similarity).

        Returns value in [0, 2], where 0 = identical, 2 = opposite.
        """
        return 1.0 - self.cosine_similarity(other)

    def is_similar_to(
        self, other: Embedding, threshold: float = 0.75
    ) -> bool:
        """Check if embedding is similar to another above threshold."""
        return self.cosine_similarity(other) >= threshold

    def to_bytes(self) -> bytes:
        """Serialize embedding to bytes for SQLite storage."""
        import struct

        return struct.pack(f"{len(self.vector)}f", *self.vector)

    @classmethod
    def from_bytes(cls, data: bytes) -> Embedding:
        """Deserialize embedding from bytes."""
        import struct

        count = len(data) // 4
        vector = list(struct.unpack(f"{count}f", data))
        return cls(vector)

    @classmethod
    def from_list(cls, vector: Sequence[float]) -> Embedding:
        """Create embedding from sequence of floats."""
        return cls(list(vector))

    def __len__(self) -> int:
        return self.dimension

    def __getitem__(self, index: int) -> float:
        return self.vector[index]

    def __iter__(self):
        return iter(self.vector)
