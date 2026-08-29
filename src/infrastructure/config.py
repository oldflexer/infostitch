"""Configuration Management.

Loads settings from .env file and database settings table.
Uses Pydantic Settings for validation and type coercion.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./infostitch.db", alias="DATABASE_URL"
    )

    # External APIs
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_api_key_2: str = Field(default="", alias="GEMINI_API_KEY_2")
    jina_api_key: str = Field(default="", alias="JINA_API_KEY")

    # Telegram
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")
    telegram_admin_chat_id: str = Field(default="", alias="TELEGRAM_ADMIN_CHAT_ID")

    # VK
    vk_access_token: str = Field(default="", alias="VK_ACCESS_TOKEN")
    vk_group_id: str = Field(default="", alias="VK_GROUP_ID")
    vk_album_id: str = Field(default="", alias="VK_ALBUM_ID")

    # Max
    max_bot_token: str = Field(default="", alias="MAX_BOT_TOKEN")
    max_chat_id: str = Field(default="", alias="MAX_CHAT_ID")

    # Pipeline defaults (can be overridden by DB settings)
    pipeline_interval_hours: int = Field(default=3, alias="PIPELINE_INTERVAL_HOURS")
    max_articles_per_run: int = Field(default=20, alias="MAX_ARTICLES_PER_RUN")
    jaccard_threshold: float = Field(default=0.55, alias="JACCARD_THRESHOLD")
    embedding_similarity_threshold: float = Field(
        default=0.75, alias="EMBEDDING_SIMILARITY_THRESHOLD"
    )
    embedding_model: str = Field(default="text-embedding-004", alias="EMBEDDING_MODEL")
    post_length_min: int = Field(default=700, alias="POST_LENGTH_MIN")
    post_length_max: int = Field(default=730, alias="POST_LENGTH_MAX")
    post_total_max_length: int = Field(default=1000, alias="POST_TOTAL_MAX_LENGTH")
    dedup_window_days_stage1: int = Field(default=7, alias="DEDUP_WINDOW_DAYS_STAGE1")
    dedup_window_days_stage2: int = Field(default=5, alias="DEDUP_WINDOW_DAYS_STAGE2")
    cleanup_retention_days: int = Field(default=90, alias="CLEANUP_RETENTION_DAYS")

    # Dashboard
    streamlit_server_port: int = Field(default=8501, alias="STREAMLIT_SERVER_PORT")
    streamlit_server_address: str = Field(
        default="0.0.0.0", alias="STREAMLIT_SERVER_ADDRESS"
    )
    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="admin123", alias="ADMIN_PASSWORD")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def get_gemini_api_keys(self) -> List[str]:
        """Get all configured Gemini API keys for rotation."""
        keys = [self.gemini_api_key]
        if self.gemini_api_key_2:
            keys.append(self.gemini_api_key_2)
        return [k for k in keys if k]

    def get_channel_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get channel configurations from environment."""
        configs = {}

        if self.telegram_bot_token and self.telegram_chat_id:
            configs["telegram"] = {
                "chat_id": self.telegram_chat_id,
                "bot_token_ref": "TELEGRAM_BOT_TOKEN",
            }

        if self.vk_access_token and self.vk_group_id:
            configs["vk"] = {
                "group_id": self.vk_group_id,
                "access_token_ref": "VK_ACCESS_TOKEN",
                "album_id": self.vk_album_id,
            }

        if self.max_bot_token and self.max_chat_id:
            configs["max"] = {
                "chat_id": self.max_chat_id,
                "bot_token_ref": "MAX_BOT_TOKEN",
            }

        return configs


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


class DatabaseSettings:
    """Settings loaded from database settings table.

    These override environment variable defaults at runtime.
    """

    def __init__(self, settings_dict: Dict[str, str]):
        self._settings = settings_dict

    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value with type coercion."""
        value = self._settings.get(key)
        if value is None:
            return default

        # Try to parse as JSON first (for arrays, objects)
        try:
            import json

            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

        # Try boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Try int
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        return value

    def get_int(self, key: str, default: int = 0) -> int:
        return int(self.get(key, default))

    def get_float(self, key: str, default: float = 0.0) -> float:
        return float(self.get(key, default))

    def get_bool(self, key: str, default: bool = False) -> bool:
        val = self.get(key, default)
        if isinstance(val, bool):
            return val
        return str(val).lower() == "true"

    def get_list(self, key: str, default: List = None) -> List:
        val = self.get(key, default or [])
        if isinstance(val, list):
            return val
        return [val] if val else []


# Default settings that match .env.example
DEFAULT_SETTINGS = {
    "pipeline_interval_hours": "3",
    "max_articles_per_run": "20",
    "jaccard_threshold": "0.55",
    "embedding_similarity_threshold": "0.75",
    "embedding_model": "text-embedding-004",
    "post_length_min": "700",
    "post_length_max": "730",
    "post_total_max_length": "1000",
    "dedup_window_days_stage1": "7",
    "dedup_window_days_stage2": "5",
    "template_pool": '["news_brief", "deep_dive", "quick_take", "expert_opinion", "case_study", "trend_analysis", "tool_review", "research_summary", "industry_news", "tutorial_style"]',
    "default_template_id": "news_brief",
    "jina_api_key_ref": "JINA_API_KEY",
    "notification_chat_id": "",
    "cleanup_retention_days": "90",
}