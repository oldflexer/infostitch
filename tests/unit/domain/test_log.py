"""Unit tests for Log entity."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from domain.entities.log import Log


class TestLog:
    """Tests for Log entity."""

    def test_create_log(self):
        """Test creating a log entry."""
        log = Log(
            id=1,
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            module="test.module",
            message="Test message",
            context_json={"key": "value"},
            user_id=1,
        )
        
        assert log.id == 1
        assert log.level == "INFO"
        assert log.module == "test.module"
        assert log.message == "Test message"
        assert log.context_json == {"key": "value"}
        assert log.user_id == 1

    def test_log_levels(self):
        """Test valid log levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log = Log(
                id=1,
                timestamp=datetime.now(timezone.utc),
                level=level,
                module="test.module",
                message="Test message",
            )
            assert log.level == level