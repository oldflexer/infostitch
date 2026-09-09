"""Unit tests for metrics infrastructure."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


from infrastructure.logging.metrics import (
    MetricsContext,
    increment_counter,
    init_metrics,
    observe_histogram,
    set_gauge,
)


class TestMetricsContext:
    """Tests for MetricsContext."""

    def test_metrics_context_enter_exit(self):
        """Test MetricsContext context manager."""
        mock_histogram = MagicMock()
        mock_timer = MagicMock()
        mock_histogram.labels.return_value.time.return_value = mock_timer

        with MetricsContext(mock_histogram, labels={"step": "test"}) as ctx:
            assert ctx.histogram == mock_histogram
            assert ctx.labels == {"step": "test"}
            assert ctx.timer == mock_timer
            mock_histogram.labels.assert_called_once_with(step="test")
            mock_timer.__enter__.assert_called_once()

        mock_timer.__exit__.assert_called_once()

    def test_metrics_context_no_labels(self):
        """Test MetricsContext without labels."""
        mock_histogram = MagicMock()
        mock_timer = MagicMock()
        mock_histogram.labels.return_value.time.return_value = mock_timer

        with MetricsContext(mock_histogram) as ctx:
            assert ctx.labels == {}
            mock_histogram.labels.assert_called_once_with()

    def test_metrics_context_with_exception(self):
        """Test MetricsContext handles exceptions."""
        mock_histogram = MagicMock()
        mock_timer = MagicMock()
        mock_histogram.labels.return_value.time.return_value = mock_timer

        try:
            with MetricsContext(mock_histogram):
                raise ValueError("test error")
        except ValueError:
            pass

        mock_timer.__exit__.assert_called_once()


class TestIncrementCounter:
    """Tests for increment_counter."""

    def test_increment_counter_with_labels(self):
        """Test increment_counter with labels."""
        mock_counter = MagicMock()
        mock_labeled = MagicMock()
        mock_counter.labels.return_value = mock_labeled

        increment_counter(mock_counter, labels={"service": "test"}, value=5.0)

        mock_counter.labels.assert_called_once_with(service="test")
        mock_labeled.inc.assert_called_once_with(5.0)

    def test_increment_counter_without_labels(self):
        """Test increment_counter without labels."""
        mock_counter = MagicMock()

        increment_counter(mock_counter, value=3.0)

        mock_counter.inc.assert_called_once_with(3.0)

    def test_increment_counter_default_value(self):
        """Test increment_counter with default value."""
        mock_counter = MagicMock()

        increment_counter(mock_counter)

        mock_counter.inc.assert_called_once_with(1.0)


class TestObserveHistogram:
    """Tests for observe_histogram."""

    def test_observe_histogram_with_labels(self):
        """Test observe_histogram with labels."""
        mock_histogram = MagicMock()
        mock_labeled = MagicMock()
        mock_histogram.labels.return_value = mock_labeled

        observe_histogram(mock_histogram, 1.5, labels={"service": "test"})

        mock_histogram.labels.assert_called_once_with(service="test")
        mock_labeled.observe.assert_called_once_with(1.5)

    def test_observe_histogram_without_labels(self):
        """Test observe_histogram without labels."""
        mock_histogram = MagicMock()

        observe_histogram(mock_histogram, 2.5)

        mock_histogram.observe.assert_called_once_with(2.5)


class TestSetGauge:
    """Tests for set_gauge."""

    def test_set_gauge_with_labels(self):
        """Test set_gauge with labels."""
        mock_gauge = MagicMock()
        mock_labeled = MagicMock()
        mock_gauge.labels.return_value = mock_labeled

        set_gauge(mock_gauge, 10.0, labels={"queue": "test"})

        mock_gauge.labels.assert_called_once_with(queue="test")
        mock_labeled.set.assert_called_once_with(10.0)

    def test_set_gauge_without_labels(self):
        """Test set_gauge without labels."""
        mock_gauge = MagicMock()

        set_gauge(mock_gauge, 5.0)

        mock_gauge.set.assert_called_once_with(5.0)


class TestInitMetrics:
    """Tests for init_metrics."""

    @patch("infrastructure.logging.metrics.get_settings")
    @patch("infrastructure.logging.metrics.app_info")
    def test_init_metrics(self, mock_app_info, mock_get_settings):
        """Test init_metrics initializes app info."""
        mock_settings = MagicMock()
        mock_settings.app_env = "test"
        mock_get_settings.return_value = mock_settings

        init_metrics()

        mock_app_info.info.assert_called_once_with({
            "version": "0.1.0",
            "environment": "test",
        })