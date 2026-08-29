"""User Repository Interface.

Defines the contract for user data access.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.user import User


class UserRepository(ABC):
    """Abstract repository for User entities."""

    @abstractmethod
    async def create(
        self, username: str, password: str, role: str = "admin"
    ) -> User:
        """Create a new user with hashed password."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        ...

    @abstractmethod
    async def get_all(self) -> List[User]:
        """Get all users."""
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        ...

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete a user."""
        ...

    @abstractmethod
    async def verify_password(self, username: str, password: str) -> Optional[User]:
        """Verify password and return user if valid."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Count total users."""
        ...