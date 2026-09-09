"""Unit tests for logging infrastructure."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


from infrastructure.logging.logger import (
    LoggingContext,
    add_correlation_id,
    add_level,
    add_timestamp,
    clear_correlation_id,
    get_correlation_id,
    get_logger,
    set_correlation_id,
    setup_logging,
)


class TestCorrelationId:
    """Tests for correlation ID functions."""

    def test_get_correlation_id_generates_new(self):
        """Test get_correlation_id generates new ID when none exists."""
        clear_correlation_id()
        cid = get_correlation_id()
        assert cid is not None
        assert len(cid) == 8

    def test_get_correlation_id_returns_existing(self):
        """Test get_correlation_id returns existing ID."""
        clear_correlation_id()
        cid1 = get_correlation_id()
        cid2 = get_correlation_id()
        assert cid1 == cid2

    def test_set_correlation_id(self):
        """Test set_correlation_id sets custom ID."""
        cid = set_correlation_id("custom-id")
        assert cid == "custom-id"
        assert get_correlation_id() == "custom-id"

    def test_set_correlation_id_generates_when_none(self):
        """Test set_correlation_id generates ID when None provided."""
        cid = set_correlation_id(None)
        assert cid is not None
        assert len(cid) == 8
        assert get_correlation_id() == cid

    def test_clear_correlation_id(self):
        """Test clear_correlation_id clears the ID."""
        set_correlation_id("test-id")
        clear_correlation_id()
        # Should generate new one
        cid = get_correlation_id()
        assert cid != "test-id"


class TestLogProcessors:
    """Tests for log processors."""

    def test_add_correlation_id(self):
        """Test add_correlation_id processor."""
        logger = MagicMock()
        event_dict = {}
        result = add_correlation_id(logger, "info", event_dict)
        assert "correlation_id" in result
        assert len(result["correlation_id"]) == 8

    def test_add_timestamp(self):
        """Test add_timestamp processor."""
        logger = MagicMock()
        event_dict = {}
        result = add_timestamp(logger, "info", event_dict)
        assert "timestamp" in result
        assert "T" in result["timestamp"]  # ISO format

    def test_add_level(self):
        """Test add_level processor."""
        logger = MagicMock()
        event_dict = {}
        result = add_level(logger, "info", event_dict)
        assert result["level"] == "INFO"

        event_dict = {}
        result = add_level(logger, "error", event_dict)
        assert result["level"] == "ERROR"


class TestSetupLogging:
    """Tests for setup_logging."""

    @patch("infrastructure.logging.logger.get_settings")
    @patch("structlog.configure")
    @patch("logging.basicConfig")
    def test_setup_logging_json(self, mock_basic_config, mock_structlog_configure, mock_get_settings):
        """Test setup_logging with JSON format."""
        mock_settings = MagicMock()
        mock_settings.log_level = "INFO"
        mock_settings.log_format = "json"
        mock_get_settings.return_value = mock_settings

        setup_logging()

        mock_basic_config.assert_called_once()
        mock_structlog_configure.assert_called_once()

    @patch("infrastructure.logging.logger.get_settings")
    @patch("structlog.configure")
    @patch("logging.basicConfig")
    def test_setup_logging_console(self, mock_basic_config, mock_structlog_configure, mock_get_settings):
        """Test setup_logging with console format."""
        mock_settings = MagicMock()
        mock_settings.log_level = "DEBUG"
        mock_settings.log_format = "console"
        mock_get_settings.return_value = mock_settings

        setup_logging()

        mock_basic_config.assert_called_once()
        mock_structlog_configure.assert_called_once()


class TestGetLogger:
    """Tests for get_logger."""

    def test_get_logger(self):
        """Test get_logger returns structlog logger."""
        logger = get_logger("test.module")
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")


class TestLoggingContext:
    """Tests for LoggingContext."""

    def test_logging_context_enter_exit(self):
        """Test LoggingContext context manager."""
        with LoggingContext(key1="value1", key2="value2") as ctx:
            assert ctx.kwargs == {"key1": "value1", "key2": "value2"}
            assert ctx.token is not None

    def test_logging_context_with_exception(self):
        """Test LoggingContext handles exceptions."""
        try:
            with LoggingContext(key="value"):
                raise ValueError("test error")
        except ValueError:
            pass
        # Should not raise