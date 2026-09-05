"""Unit tests for database repositories - Log, Setting, and User."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from domain.entities.log import Log
from domain.entities.user import User
from infrastructure.db.repositories.log_repo import (
    LogFilters,
    Pagination,
    SqlAlchemyLogRepository,
)
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository
from infrastructure.db.repositories.user_repo import SqlAlchemyUserRepository


class TestSqlAlchemyLogRepository:
    """Tests for SqlAlchemyLogRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemyLogRepository(mock_session)

    @pytest.fixture
    def sample_log(self):
        """Create sample log."""
        return Log(
            id=1,
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            module="test.module",
            message="Test message",
            context_json={"key": "value"},
            user_id=1,
        )

    @pytest.mark.asyncio
    async def test_to_entity(self, repo):
        """Test _to_entity conversion."""
        model = MagicMock()
        model.id = 1
        model.timestamp = datetime.now(timezone.utc)
        model.level = "INFO"
        model.module = "test.module"
        model.message = "Test message"
        model.context_json = {"key": "value"}
        model.user_id = 1

        entity = repo._to_entity(model)

        assert entity.id == 1
        assert entity.level == "INFO"
        assert entity.module == "test.module"
        assert entity.message == "Test message"
        assert entity.context_json == {"key": "value"}
        assert entity.user_id == 1

    @pytest.mark.asyncio
    async def test_add(self, repo, sample_log, mock_session):
        """Test add log."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = sample_log.timestamp
        mock_model.level = "INFO"
        mock_model.module = "test.module"
        mock_model.message = "Test message"
        mock_model.context_json = {"key": "value"}
        mock_model.user_id = 1

        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(return_value=mock_model)

        with patch("infrastructure.db.repositories.log_repo.LogModel", return_value=mock_model):
            result = await repo.add(sample_log)

        assert result.level == "INFO"
        assert result.module == "test.module"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, mock_session):
        """Test get_by_id."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "INFO"
        mock_model.module = "test.module"
        mock_model.message = "Test message"
        mock_model.context_json = {"key": "value"}
        mock_model.user_id = 1

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.level == "INFO"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo, mock_session):
        """Test get_by_id when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_logs_no_filters(self, repo, mock_session):
        """Test get_logs without filters."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "INFO"
        mock_model.module = "test.module"
        mock_model.message = "Test message"
        mock_model.context_json = {"key": "value"}
        mock_model.user_id = 1

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_logs()

        assert len(result) == 1
        assert result[0].level == "INFO"

    @pytest.mark.asyncio
    async def test_get_logs_with_level_filter(self, repo, mock_session):
        """Test get_logs with level filter."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "ERROR"
        mock_model.module = "test.module"
        mock_model.message = "Error message"
        mock_model.context_json = {}
        mock_model.user_id = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        filters = LogFilters(level="ERROR")
        result = await repo.get_logs(filters=filters)

        assert len(result) == 1
        assert result[0].level == "ERROR"

    @pytest.mark.asyncio
    async def test_get_logs_with_module_filter(self, repo, mock_session):
        """Test get_logs with module filter."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "INFO"
        mock_model.module = "specific.module"
        mock_model.message = "Test message"
        mock_model.context_json = {}
        mock_model.user_id = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        filters = LogFilters(module="specific.module")
        result = await repo.get_logs(filters=filters)

        assert len(result) == 1
        assert result[0].module == "specific.module"

    @pytest.mark.asyncio
    async def test_get_logs_with_time_filters(self, repo, mock_session):
        """Test get_logs with time filters."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "INFO"
        mock_model.module = "test.module"
        mock_model.message = "Test message"
        mock_model.context_json = {}
        mock_model.user_id = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        start = datetime.now(timezone.utc) - timedelta(hours=1)
        end = datetime.now(timezone.utc)
        filters = LogFilters(start_time=start, end_time=end)
        result = await repo.get_logs(filters=filters)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_logs_with_correlation_id(self, repo, mock_session):
        """Test get_logs with correlation_id filter."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "INFO"
        mock_model.module = "test.module"
        mock_model.message = "Test message"
        mock_model.context_json = {"correlation_id": "abc123"}
        mock_model.user_id = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        filters = LogFilters(correlation_id="abc123")
        result = await repo.get_logs(filters=filters)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_logs_with_search_query(self, repo, mock_session):
        """Test get_logs with search query."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "INFO"
        mock_model.module = "test.module"
        mock_model.message = "Test error message"
        mock_model.context_json = {}
        mock_model.user_id = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        filters = LogFilters(search_query="error")
        result = await repo.get_logs(filters=filters)

        assert len(result) == 1
        assert "error" in result[0].message.lower()

    @pytest.mark.asyncio
    async def test_get_logs_with_pagination(self, repo, mock_session):
        """Test get_logs with pagination."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "INFO"
        mock_model.module = "test.module"
        mock_model.message = "Test message"
        mock_model.context_json = {}
        mock_model.user_id = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        pagination = Pagination(page=2, page_size=10)
        result = await repo.get_logs(pagination=pagination)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_count_logs(self, repo, mock_session):
        """Test count_logs."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_session.execute.return_value = mock_result

        result = await repo.count_logs()

        assert result == 42

    @pytest.mark.asyncio
    async def test_count_logs_with_filters(self, repo, mock_session):
        """Test count_logs with filters."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result

        filters = LogFilters(level="ERROR")
        result = await repo.count_logs(filters=filters)

        assert result == 5

    @pytest.mark.asyncio
    async def test_get_log_stats(self, repo, mock_session):
        """Test get_log_stats."""
        total_result = MagicMock()
        total_result.scalar.return_value = 100

        level_result = MagicMock()
        # Create mock objects with level attribute
        level_row1 = MagicMock()
        level_row1.level = "INFO"
        level_row1.__getitem__ = lambda self, idx: 50 if idx == 1 else "INFO"
        level_row2 = MagicMock()
        level_row2.level = "ERROR"
        level_row2.__getitem__ = lambda self, idx: 30 if idx == 1 else "ERROR"
        level_row3 = MagicMock()
        level_row3.level = "WARNING"
        level_row3.__getitem__ = lambda self, idx: 20 if idx == 1 else "WARNING"
        level_result.all.return_value = [level_row1, level_row2, level_row3]

        module_result = MagicMock()
        module_row1 = MagicMock()
        module_row1.module = "module1"
        module_row1.__getitem__ = lambda self, idx: 40 if idx == 1 else "module1"
        module_row2 = MagicMock()
        module_row2.module = "module2"
        module_row2.__getitem__ = lambda self, idx: 30 if idx == 1 else "module2"
        module_row3 = MagicMock()
        module_row3.module = "module3"
        module_row3.__getitem__ = lambda self, idx: 30 if idx == 1 else "module3"
        module_result.all.return_value = [module_row1, module_row2, module_row3]

        mock_session.execute.side_effect = [total_result, level_result, module_result]

        result = await repo.get_log_stats()

        assert result["total"] == 100
        assert result["by_level"]["INFO"] == 50
        assert result["by_level"]["ERROR"] == 30
        assert result["by_module"]["module1"] == 40

    @pytest.mark.asyncio
    async def test_get_log_stats_with_time_range(self, repo, mock_session):
        """Test get_log_stats with time range."""
        total_result = MagicMock()
        total_result.scalar.return_value = 50

        level_result = MagicMock()
        level_row = MagicMock()
        level_row.level = "INFO"
        level_row.__getitem__ = lambda self, idx: 50 if idx == 1 else "INFO"
        level_result.all.return_value = [level_row]

        module_result = MagicMock()
        module_row = MagicMock()
        module_row.module = "module1"
        module_row.__getitem__ = lambda self, idx: 50 if idx == 1 else "module1"
        module_result.all.return_value = [module_row]

        mock_session.execute.side_effect = [total_result, level_result, module_result]

        start = datetime.now(timezone.utc) - timedelta(days=1)
        end = datetime.now(timezone.utc)
        result = await repo.get_log_stats(start_time=start, end_time=end)

        assert result["total"] == 50

    @pytest.mark.asyncio
    async def test_search_logs(self, repo, mock_session):
        """Test search_logs delegates to get_logs."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.timestamp = datetime.now(timezone.utc)
        mock_model.level = "INFO"
        mock_model.module = "test.module"
        mock_model.message = "Search result"
        mock_model.context_json = {}
        mock_model.user_id = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.search_logs("search term")

        assert len(result) == 1
        assert result[0].message == "Search result"



class TestSqlAlchemySettingRepository:
    """Tests for SqlAlchemySettingRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        session = AsyncMock()
        session.bind = MagicMock()
        session.bind.dialect.name = "sqlite"
        return session

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemySettingRepository(mock_session)

    @pytest.mark.asyncio
    async def test_get(self, repo, mock_session):
        """Test get setting."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "test_value"
        mock_session.execute.return_value = mock_result

        result = await repo.get("test_key")

        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_get_not_found(self, repo, mock_session):
        """Test get setting not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repo.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repo, mock_session):
        """Test get_all settings."""
        mock_result = MagicMock()
        # Create mock objects with key and value attributes
        row1 = MagicMock()
        row1.key = "key1"
        row1.value = "value1"
        row2 = MagicMock()
        row2.key = "key2"
        row2.value = "value2"
        mock_result.all.return_value = [row1, row2]
        mock_session.execute.return_value = mock_result

        result = await repo.get_all()

        assert result == {"key1": "value1", "key2": "value2"}

    @pytest.mark.asyncio
    async def test_set(self, repo, mock_session):
        """Test set setting."""
        mock_session.execute = AsyncMock()

        await repo.set("test_key", "test_value", "Test description")

        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete(self, repo, mock_session):
        """Test delete setting."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repo.delete("test_key")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repo, mock_session):
        """Test delete setting not found."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repo.delete("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists(self, repo, mock_session):
        """Test exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "key1"
        mock_session.execute.return_value = mock_result

        result = await repo.exists("key1")

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_not_found(self, repo, mock_session):
        """Test exists not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repo.exists("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_bulk_set(self, repo, mock_session):
        """Test bulk_set."""
        mock_session.execute = AsyncMock()

        await repo.bulk_set({"key1": "value1", "key2": "value2"})

        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_typed_string(self, repo, mock_session):
        """Test get_typed with string."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "hello"
        mock_session.execute.return_value = mock_result

        result = await repo.get_typed("test_key")

        assert result == "hello"

    @pytest.mark.asyncio
    async def test_get_typed_json(self, repo, mock_session):
        """Test get_typed with JSON."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = '{"key": "value"}'
        mock_session.execute.return_value = mock_result

        result = await repo.get_typed("test_key")

        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_typed_boolean(self, repo, mock_session):
        """Test get_typed with boolean."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "true"
        mock_session.execute.return_value = mock_result

        result = await repo.get_typed("test_key")

        assert result is True

    @pytest.mark.asyncio
    async def test_get_typed_int(self, repo, mock_session):
        """Test get_typed with int."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "42"
        mock_session.execute.return_value = mock_result

        result = await repo.get_typed("test_key")

        assert result == 42

    @pytest.mark.asyncio
    async def test_get_typed_float(self, repo, mock_session):
        """Test get_typed with float."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "3.14"
        mock_session.execute.return_value = mock_result

        result = await repo.get_typed("test_key")

        assert result == 3.14

    @pytest.mark.asyncio
    async def test_get_typed_default(self, repo, mock_session):
        """Test get_typed with default."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repo.get_typed("nonexistent", default="default_value")

        assert result == "default_value"

    @pytest.mark.asyncio
    async def test_initialize_defaults(self, repo, mock_session):
        """Test initialize_defaults."""
        mock_session.execute = AsyncMock()

        exists_results = [MagicMock(), MagicMock()]
        exists_results[0].scalar_one_or_none.return_value = None
        exists_results[1].scalar_one_or_none.return_value = "existing"

        mock_session.execute.side_effect = [
            exists_results[0],
            MagicMock(),
            exists_results[1],
        ]

        await repo.initialize_defaults({"key1": "value1", "key2": "value2"})

        assert mock_session.execute.call_count == 3



class TestSqlAlchemyUserRepository:
    """Tests for SqlAlchemyUserRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        """Create repository instance."""
        return SqlAlchemyUserRepository(mock_session)

    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            id=1,
            username="testuser",
            password_hash="hashed_password",
            role="admin",
            created_at=datetime.now(timezone.utc),
            last_login=None,
        )

    @pytest.mark.asyncio
    async def test_to_entity(self, repo):
        """Test _to_entity conversion."""
        model = MagicMock()
        model.id = 1
        model.username = "testuser"
        model.password_hash = "hashed_password"
        model.role = "admin"
        model.created_at = datetime.now(timezone.utc)
        model.last_login = None

        entity = repo._to_entity(model)

        assert entity.id == 1
        assert entity.username == "testuser"
        assert entity.password_hash == "hashed_password"
        assert entity.role == "admin"

    @pytest.mark.asyncio
    async def test_to_model(self, repo, sample_user):
        """Test _to_model conversion."""
        model = repo._to_model(sample_user)

        assert model.id == 1
        assert model.username == "testuser"
        assert model.password_hash == "hashed_password"
        assert model.role == "admin"

    @pytest.mark.asyncio
    async def test_create(self, repo, mock_session):
        """Test create user."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.username = "newuser"
        mock_model.password_hash = "hashed_password"
        mock_model.role = "admin"
        mock_model.created_at = datetime.now(timezone.utc)
        mock_model.last_login = None

        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock(return_value=mock_model)

        with patch("infrastructure.db.repositories.user_repo.UserModel", return_value=mock_model):
            with patch("bcrypt.hashpw", return_value=b"hashed_password"):
                with patch("bcrypt.gensalt", return_value=b"$2b$12$salt"):
                    result = await repo.create("newuser", "password123", "admin")

        assert result.username == "newuser"
        assert result.role == "admin"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, mock_session):
        """Test get_by_id."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.username = "testuser"
        mock_model.password_hash = "hashed_password"
        mock_model.role = "admin"
        mock_model.created_at = datetime.now(timezone.utc)
        mock_model.last_login = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(1)

        assert result is not None
        assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo, mock_session):
        """Test get_by_id not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_id(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_username(self, repo, mock_session):
        """Test get_by_username."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.username = "testuser"
        mock_model.password_hash = "hashed_password"
        mock_model.role = "admin"
        mock_model.created_at = datetime.now(timezone.utc)
        mock_model.last_login = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.execute.return_value = mock_result

        result = await repo.get_by_username("testuser")

        assert result is not None
        assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_all(self, repo, mock_session):
        """Test get_all."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.username = "testuser"
        mock_model.password_hash = "hashed_password"
        mock_model.role = "admin"
        mock_model.created_at = datetime.now(timezone.utc)
        mock_model.last_login = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        mock_session.execute.return_value = mock_result

        result = await repo.get_all()

        assert len(result) == 1
        assert result[0].username == "testuser"

    @pytest.mark.asyncio
    async def test_update(self, repo, sample_user, mock_session):
        """Test update user."""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.username = "olduser"
        mock_model.password_hash = "old_hash"
        mock_model.role = "user"
        mock_model.last_login = None

        mock_session.get.return_value = mock_model
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        sample_user.username = "updateduser"
        sample_user.role = "admin"
        result = await repo.update(sample_user)

        assert result.username == "updateduser"
        assert result.role == "admin"
        assert mock_model.username == "updateduser"
        assert mock_model.role == "admin"
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self, repo, sample_user, mock_session):
        """Test update when user not found."""
        mock_session.get.return_value = None

        with pytest.raises(ValueError, match="User 1 not found"):
            await repo.update(sample_user)

    @pytest.mark.asyncio
    async def test_delete(self, repo, mock_session):
        """Test delete user."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repo.delete(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repo, mock_session):
        """Test delete user not found."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repo.delete(999)
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_password_success(self, repo, mock_session):
        """Test verify_password success."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.password_hash = "hashed_password"
        mock_user.role = "admin"
        mock_user.created_at = datetime.now(timezone.utc)
        mock_user.last_login = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        with patch("bcrypt.checkpw", return_value=True):
            result = await repo.verify_password("testuser", "password123")

        assert result is not None
        assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_verify_password_wrong_password(self, repo, mock_session):
        """Test verify_password wrong password."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.password_hash = "hashed_password"
        mock_user.role = "admin"
        mock_user.created_at = datetime.now(timezone.utc)
        mock_user.last_login = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        with patch("bcrypt.checkpw", return_value=False):
            result = await repo.verify_password("testuser", "wrong_password")

        assert result is None

    @pytest.mark.asyncio
    async def test_verify_password_user_not_found(self, repo, mock_session):
        """Test verify_password user not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repo.verify_password("nonexistent", "password123")

        assert result is None

    @pytest.mark.asyncio
    async def test_count(self, repo, mock_session):
        """Test count users."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result

        result = await repo.count()

        assert result == 5
