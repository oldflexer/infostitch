"""Unit tests for User entity."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from domain.entities.user import User


class TestUser:
    """Tests for User entity."""

    def test_create_user(self):
        """Test creating a user."""
        import bcrypt
        password_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
        
        user = User(
            id=1,
            username="testuser",
            password_hash=password_hash,
            role="admin",
            created_at=datetime.now(timezone.utc),
        )
        
        assert user.id == 1
        assert user.username == "testuser"
        assert user.password_hash == password_hash
        assert user.role == "admin"

    def test_create_user_invalid_role_raises(self):
        """Test that invalid role raises ValueError."""
        import bcrypt
        password_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
        
        with pytest.raises(ValueError, match="Invalid role"):
            User(
                id=1,
                username="testuser",
                password_hash=password_hash,
                role="invalid",
                created_at=datetime.now(timezone.utc),
            )

    def test_update_last_login(self):
        """Test update_last_login returns new user with updated last_login."""
        import bcrypt
        password_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
        
        user = User(
            id=1,
            username="testuser",
            password_hash=password_hash,
            role="admin",
            created_at=datetime.now(timezone.utc),
        )
        
        assert user.last_login is None
        updated = user.update_last_login()
        assert updated.last_login is not None
        assert updated.id == user.id
        assert updated.username == user.username

    def test_to_dict_excludes_password_hash(self):
        """Test that to_dict excludes password hash."""
        import bcrypt
        password_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
        
        user = User(
            id=1,
            username="testuser",
            password_hash=password_hash,
            role="admin",
            created_at=datetime.now(timezone.utc),
        )
        
        user_dict = user.to_dict()
        assert "password_hash" not in user_dict
        assert user_dict["username"] == "testuser"
        assert user_dict["role"] == "admin"