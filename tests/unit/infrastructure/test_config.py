"""Unit tests for config module."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from infrastructure.config import (
    DEFAULT_SETTINGS,
    DatabaseSettings,
    Settings,
    get_settings,
)


class TestSettings:
    """Tests for Settings class."""

    def test_default_values(self):
        """Test default values are set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()

            assert settings.app_env == "development"
            assert settings.log_level == "INFO"
            assert settings.log_format == "json"
            assert settings.database_url == "sqlite+aiosqlite:///./infostitch.db"
            assert settings.gemini_api_key == ""
            assert settings.gemini_api_key_2 == ""
            assert settings.jina_api_key == ""
            assert settings.telegram_bot_token == ""
            assert settings.telegram_chat_id == ""
            assert settings.telegram_admin_chat_id == ""
            assert settings.vk_access_token == ""
            assert settings.vk_group_id == ""
            assert settings.vk_album_id == ""
            assert settings.max_bot_token == ""
            assert settings.max_chat_id == ""
            assert settings.pipeline_interval_hours == 3
            assert settings.max_articles_per_run == 20
            assert settings.jaccard_threshold == 0.55
            assert settings.embedding_similarity_threshold == 0.75
            assert settings.embedding_model == "text-embedding-004"
            assert settings.post_length_min == 700
            assert settings.post_length_max == 730
            assert settings.post_total_max_length == 1000
            assert settings.dedup_window_days_stage1 == 7
            assert settings.dedup_window_days_stage2 == 5
            assert settings.cleanup_retention_days == 90
            assert settings.streamlit_server_port == 8501
            assert settings.streamlit_server_address == "0.0.0.0"
            assert settings.admin_username == "admin"
            assert settings.admin_password == "admin123"

    def test_env_override(self):
        """Test environment variables override defaults."""
        env = {
            "APP_ENV": "production",
            "LOG_LEVEL": "DEBUG",
            "DATABASE_URL": "postgresql://user:pass@localhost/db",
            "GEMINI_API_KEY": "test-key-1",
            "GEMINI_API_KEY_2": "test-key-2",
            "JINA_API_KEY": "jina-key",
            "TELEGRAM_BOT_TOKEN": "tg-token",
            "TELEGRAM_CHAT_ID": "tg-chat",
            "TELEGRAM_ADMIN_CHAT_ID": "tg-admin",
            "VK_ACCESS_TOKEN": "vk-token",
            "VK_GROUP_ID": "vk-group",
            "VK_ALBUM_ID": "vk-album",
            "MAX_BOT_TOKEN": "max-token",
            "MAX_CHAT_ID": "max-chat",
            "PIPELINE_INTERVAL_HOURS": "6",
            "MAX_ARTICLES_PER_RUN": "50",
            "JACCARD_THRESHOLD": "0.6",
            "EMBEDDING_SIMILARITY_THRESHOLD": "0.8",
            "EMBEDDING_MODEL": "text-embedding-005",
            "POST_LENGTH_MIN": "800",
            "POST_LENGTH_MAX": "850",
            "POST_TOTAL_MAX_LENGTH": "1200",
            "DEDUP_WINDOW_DAYS_STAGE1": "14",
            "DEDUP_WINDOW_DAYS_STAGE2": "10",
            "CLEANUP_RETENTION_DAYS": "180",
            "STREAMLIT_SERVER_PORT": "8502",
            "STREAMLIT_SERVER_ADDRESS": "127.0.0.1",
            "ADMIN_USERNAME": "custom_admin",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()

            assert settings.app_env == "production"
            assert settings.log_level == "DEBUG"
            assert settings.database_url == "postgresql://user:pass@localhost/db"
            assert settings.gemini_api_key == "test-key-1"
            assert settings.gemini_api_key_2 == "test-key-2"
            assert settings.jina_api_key == "jina-key"
            assert settings.telegram_bot_token == "tg-token"
            assert settings.telegram_chat_id == "tg-chat"
            assert settings.telegram_admin_chat_id == "tg-admin"
            assert settings.vk_access_token == "vk-token"
            assert settings.vk_group_id == "vk-group"
            assert settings.vk_album_id == "vk-album"
            assert settings.max_bot_token == "max-token"
            assert settings.max_chat_id == "max-chat"
            assert settings.pipeline_interval_hours == 6
            assert settings.max_articles_per_run == 50
            assert settings.jaccard_threshold == 0.6
            assert settings.embedding_similarity_threshold == 0.8
            assert settings.embedding_model == "text-embedding-005"
            assert settings.post_length_min == 800
            assert settings.post_length_max == 850
            assert settings.post_total_max_length == 1200
            assert settings.dedup_window_days_stage1 == 14
            assert settings.dedup_window_days_stage2 == 10
            assert settings.cleanup_retention_days == 180
            assert settings.streamlit_server_port == 8502
            assert settings.streamlit_server_address == "127.0.0.1"
            assert settings.admin_username == "custom_admin"
            assert settings.admin_password == "secure_password"

    def test_is_development_property(self):
        """Test is_development property."""
        with patch.dict(os.environ, {"APP_ENV": "development"}, clear=True):
            settings = Settings()
            assert settings.is_development is True
            assert settings.is_production is False

        with patch.dict(os.environ, {"APP_ENV": "production"}, clear=True):
            settings = Settings()
            assert settings.is_development is False
            assert settings.is_production is True

        with patch.dict(os.environ, {"APP_ENV": "staging"}, clear=True):
            settings = Settings()
            assert settings.is_development is False
            assert settings.is_production is False

    def test_get_gemini_api_keys(self):
        """Test get_gemini_api_keys method."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "key1", "GEMINI_API_KEY_2": "key2"}, clear=True):
            settings = Settings()
            keys = settings.get_gemini_api_keys()
            assert keys == ["key1", "key2"]

        with patch.dict(os.environ, {"GEMINI_API_KEY": "key1"}, clear=True):
            settings = Settings()
            keys = settings.get_gemini_api_keys()
            assert keys == ["key1"]

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            keys = settings.get_gemini_api_keys()
            assert keys == []

    def test_validate_all_configured(self):
        """Test validate when all required settings are configured."""
        env = {
            "APP_ENV": "production",
            "GEMINI_API_KEY": "valid-key",
            "JINA_API_KEY": "valid-jina",
            "TELEGRAM_BOT_TOKEN": "valid-tg-token",
            "TELEGRAM_CHAT_ID": "valid-chat",
            "VK_ACCESS_TOKEN": "valid-vk-token",
            "VK_GROUP_ID": "valid-group",
            "MAX_BOT_TOKEN": "valid-max-token",
            "MAX_CHAT_ID": "valid-max-chat",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert missing == []

    def test_validate_missing_gemini(self):
        """Test validate with missing Gemini API key."""
        env = {
            "APP_ENV": "production",
            "JINA_API_KEY": "valid-jina",
            "TELEGRAM_BOT_TOKEN": "valid-tg-token",
            "TELEGRAM_CHAT_ID": "valid-chat",
            "VK_ACCESS_TOKEN": "valid-vk-token",
            "VK_GROUP_ID": "valid-group",
            "MAX_BOT_TOKEN": "valid-max-token",
            "MAX_CHAT_ID": "valid-max-chat",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert "GEMINI_API_KEY" in missing

    def test_validate_missing_jina(self):
        """Test validate with missing Jina API key."""
        env = {
            "APP_ENV": "production",
            "GEMINI_API_KEY": "valid-key",
            "TELEGRAM_BOT_TOKEN": "valid-tg-token",
            "TELEGRAM_CHAT_ID": "valid-chat",
            "VK_ACCESS_TOKEN": "valid-vk-token",
            "VK_GROUP_ID": "valid-group",
            "MAX_BOT_TOKEN": "valid-max-token",
            "MAX_CHAT_ID": "valid-max-chat",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert "JINA_API_KEY" in missing

    def test_validate_missing_telegram(self):
        """Test validate with missing Telegram credentials."""
        env = {
            "APP_ENV": "production",
            "GEMINI_API_KEY": "valid-key",
            "JINA_API_KEY": "valid-jina",
            "VK_ACCESS_TOKEN": "valid-vk-token",
            "VK_GROUP_ID": "valid-group",
            "MAX_BOT_TOKEN": "valid-max-token",
            "MAX_CHAT_ID": "valid-max-chat",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert "TELEGRAM_BOT_TOKEN" in missing
            assert "TELEGRAM_CHAT_ID" in missing

    def test_validate_missing_vk(self):
        """Test validate with missing VK credentials."""
        env = {
            "APP_ENV": "production",
            "GEMINI_API_KEY": "valid-key",
            "JINA_API_KEY": "valid-jina",
            "TELEGRAM_BOT_TOKEN": "valid-tg-token",
            "TELEGRAM_CHAT_ID": "valid-chat",
            "MAX_BOT_TOKEN": "valid-max-token",
            "MAX_CHAT_ID": "valid-max-chat",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert "VK_ACCESS_TOKEN" in missing
            assert "VK_GROUP_ID" in missing

    def test_validate_missing_max(self):
        """Test validate with missing Max credentials."""
        env = {
            "APP_ENV": "production",
            "GEMINI_API_KEY": "valid-key",
            "JINA_API_KEY": "valid-jina",
            "TELEGRAM_BOT_TOKEN": "valid-tg-token",
            "TELEGRAM_CHAT_ID": "valid-chat",
            "VK_ACCESS_TOKEN": "valid-vk-token",
            "VK_GROUP_ID": "valid-group",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert "MAX_BOT_TOKEN" in missing
            assert "MAX_CHAT_ID" in missing

    def test_validate_no_publishers(self):
        """Test validate when no publishers are configured."""
        env = {
            "APP_ENV": "production",
            "GEMINI_API_KEY": "valid-key",
            "JINA_API_KEY": "valid-jina",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert "AT_LEAST_ONE_PUBLISHER" in missing

    def test_validate_default_admin_password(self):
        """Test validate detects default admin password."""
        env = {
            "APP_ENV": "production",
            "GEMINI_API_KEY": "valid-key",
            "JINA_API_KEY": "valid-jina",
            "TELEGRAM_BOT_TOKEN": "valid-tg-token",
            "TELEGRAM_CHAT_ID": "valid-chat",
            "VK_ACCESS_TOKEN": "valid-vk-token",
            "VK_GROUP_ID": "valid-group",
            "MAX_BOT_TOKEN": "valid-max-token",
            "MAX_CHAT_ID": "valid-max-chat",
            "ADMIN_PASSWORD": "admin123",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert "ADMIN_PASSWORD (default detected)" in missing

    def test_validate_placeholder_values(self):
        """Test validate detects placeholder values."""
        env = {
            "APP_ENV": "production",
            "GEMINI_API_KEY": "your_gemini_api_key_here",
            "JINA_API_KEY": "your_jina_api_key_here",
            "TELEGRAM_BOT_TOKEN": "your_telegram_bot_token_here",
            "TELEGRAM_CHAT_ID": "your_channel_chat_id_here",
            "VK_ACCESS_TOKEN": "your_vk_access_token_here",
            "VK_GROUP_ID": "your_vk_group_id_here",
            "MAX_BOT_TOKEN": "your_max_bot_token_here",
            "MAX_CHAT_ID": "your_max_chat_id_here",
            "ADMIN_PASSWORD": "secure_password",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            missing = settings.validate_required_secrets()
            assert "GEMINI_API_KEY" in missing
            assert "JINA_API_KEY" in missing
            assert "TELEGRAM_BOT_TOKEN" in missing
            assert "TELEGRAM_CHAT_ID" in missing
            assert "VK_ACCESS_TOKEN" in missing
            assert "VK_GROUP_ID" in missing
            assert "MAX_BOT_TOKEN" in missing
            assert "MAX_CHAT_ID" in missing



class TestDatabaseSettings:
    """Tests for DatabaseSettings class."""

    def test_get_string(self):
        """Test getting string value."""
        settings = DatabaseSettings({"key": "value"})
        assert settings.get("key") == "value"
        assert settings.get("missing", "default") == "default"

    def test_get_json_object(self):
        """Test getting JSON object."""
        settings = DatabaseSettings({"key": '{"a": 1, "b": 2}'})
        result = settings.get("key")
        assert result == {"a": 1, "b": 2}

    def test_get_json_array(self):
        """Test getting JSON array."""
        settings = DatabaseSettings({"key": "[1, 2, 3]"})
        result = settings.get("key")
        assert result == [1, 2, 3]

    def test_get_invalid_json(self):
        """Test getting invalid JSON returns string."""
        settings = DatabaseSettings({"key": "not json"})
        result = settings.get("key")
        assert result == "not json"

    def test_get_boolean_true(self):
        """Test getting boolean true."""
        settings = DatabaseSettings({"key": "true"})
        assert settings.get("key") is True

    def test_get_boolean_false(self):
        """Test getting boolean false."""
        settings = DatabaseSettings({"key": "false"})
        assert settings.get("key") is False

    def test_get_integer(self):
        """Test getting integer."""
        settings = DatabaseSettings({"key": "42"})
        assert settings.get("key") == 42

    def test_get_float(self):
        """Test getting float."""
        settings = DatabaseSettings({"key": "3.14"})
        assert settings.get("key") == 3.14

    def test_get_int_method(self):
        """Test get_int method."""
        settings = DatabaseSettings({"key": "42"})
        assert settings.get_int("key") == 42
        assert settings.get_int("missing", 10) == 10

    def test_get_float_method(self):
        """Test get_float method."""
        settings = DatabaseSettings({"key": "3.14"})
        assert settings.get_float("key") == 3.14
        assert settings.get_float("missing", 1.5) == 1.5

    def test_get_bool_method(self):
        """Test get_bool method."""
        settings = DatabaseSettings({"key": "true"})
        assert settings.get_bool("key") is True
        settings = DatabaseSettings({"key": "false"})
        assert settings.get_bool("key") is False
        settings = DatabaseSettings({"key": "yes"})
        assert settings.get_bool("key") is False
        assert settings.get_bool("missing", True) is True

    def test_get_list_method(self):
        """Test get_list method."""
        settings = DatabaseSettings({"key": "[1, 2, 3]"})
        assert settings.get_list("key") == [1, 2, 3]
        settings = DatabaseSettings({"key": "single"})
        assert settings.get_list("key") == ["single"]
        settings = DatabaseSettings({})
        assert settings.get_list("missing", [1, 2]) == [1, 2]



class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_instance(self):
        """Test get_settings returns Settings instance."""
        with patch.dict(os.environ, {}, clear=True):
            settings = get_settings()
            assert isinstance(settings, Settings)

    def test_get_settings_cached(self):
        """Test get_settings returns cached instance."""
        with patch.dict(os.environ, {}, clear=True):
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2



class TestDefaultSettings:
    """Tests for DEFAULT_SETTINGS constant."""

    def test_default_settings_structure(self):
        """Test DEFAULT_SETTINGS has expected keys."""
        expected_keys = {
            "pipeline_interval_hours",
            "max_articles_per_run",
            "jaccard_threshold",
            "embedding_similarity_threshold",
            "embedding_model",
            "post_length_min",
            "post_length_max",
            "post_total_max_length",
            "dedup_window_days_stage1",
            "dedup_window_days_stage2",
            "template_pool",
            "default_template_id",
            "jina_api_key_ref",
            "notification_chat_id",
            "cleanup_retention_days",
        }
        assert set(DEFAULT_SETTINGS.keys()) == expected_keys

    def test_default_settings_values(self):
        """Test DEFAULT_SETTINGS has correct values."""
        assert DEFAULT_SETTINGS["pipeline_interval_hours"] == "3"
        assert DEFAULT_SETTINGS["max_articles_per_run"] == "20"
        assert DEFAULT_SETTINGS["jaccard_threshold"] == "0.55"
        assert DEFAULT_SETTINGS["embedding_similarity_threshold"] == "0.75"
        assert DEFAULT_SETTINGS["embedding_model"] == "text-embedding-004"
        assert DEFAULT_SETTINGS["post_length_min"] == "700"
        assert DEFAULT_SETTINGS["post_length_max"] == "730"
        assert DEFAULT_SETTINGS["post_total_max_length"] == "1000"
        assert DEFAULT_SETTINGS["dedup_window_days_stage1"] == "7"
        assert DEFAULT_SETTINGS["dedup_window_days_stage2"] == "5"
        assert "news_brief" in DEFAULT_SETTINGS["template_pool"]
        assert DEFAULT_SETTINGS["default_template_id"] == "news_brief"
        assert DEFAULT_SETTINGS["jina_api_key_ref"] == "JINA_API_KEY"
        assert DEFAULT_SETTINGS["notification_chat_id"] == ""
        assert DEFAULT_SETTINGS["cleanup_retention_days"] == "90"
