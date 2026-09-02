"""Unit tests for Channel entity."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from domain.entities.channel import Channel


class TestChannel:
    """Tests for Channel entity."""

    def test_create_channel(self):
        """Test creating a channel."""
        channel = Channel(
            id=1,
            name="Test Telegram",
            type="telegram",
            enabled=True,
            config={"bot_token_ref": "token", "chat_id": "chat123"},
            created_at=datetime.now(timezone.utc),
        )
        
        assert channel.id == 1
        assert channel.name == "Test Telegram"
        assert channel.type == "telegram"
        assert channel.enabled is True
        assert channel.config["bot_token_ref"] == "token"
        assert channel.chat_id == "chat123"
        assert channel.token_ref == "token"

    def test_channel_types(self):
        """Test valid channel types."""
        for channel_type in ["telegram", "vk", "max"]:
            if channel_type == "telegram":
                config = {"bot_token_ref": "token", "chat_id": "chat123"}
            elif channel_type == "vk":
                config = {"access_token_ref": "token", "group_id": "group123"}
            else:  # max
                config = {"bot_token_ref": "token", "chat_id": "chat123"}
                
            channel = Channel(
                id=1,
                name=f"Test {channel_type}",
                type=channel_type,
                enabled=True,
                config=config,
                created_at=datetime.now(timezone.utc),
            )
            assert channel.type == channel_type

    def test_invalid_channel_type_raises(self):
        """Test that invalid channel type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid channel type"):
            Channel(
                id=1,
                name="Test",
                type="invalid",
                enabled=True,
                config={},
                created_at=datetime.now(timezone.utc),
            )

    def test_missing_config_raises(self):
        """Test that missing required config raises ValueError."""
        with pytest.raises(ValueError, match="Missing required config key"):
            Channel(
                id=1,
                name="Test",
                type="telegram",
                enabled=True,
                config={},  # Missing bot_token_ref and chat_id
                created_at=datetime.now(timezone.utc),
            )

    def test_toggle_enabled(self):
        """Test toggling enabled status returns new channel."""
        channel = Channel(
            id=1,
            name="Test",
            type="telegram",
            enabled=True,
            config={"bot_token_ref": "token", "chat_id": "chat123"},
            created_at=datetime.now(timezone.utc),
        )
        
        assert channel.enabled is True
        toggled = channel.toggle_enabled()
        assert toggled.enabled is False
        assert toggled.id == channel.id
        assert toggled.name == channel.name
        
        toggled2 = toggled.toggle_enabled()
        assert toggled2.enabled is True

    def test_update_config(self):
        """Test updating config returns new channel."""
        channel = Channel(
            id=1,
            name="Test",
            type="telegram",
            enabled=True,
            config={"bot_token_ref": "token", "chat_id": "chat123"},
            created_at=datetime.now(timezone.utc),
        )
        
        updated = channel.update_config({"bot_token_ref": "new_token", "chat_id": "new_chat"})
        assert updated.config["bot_token_ref"] == "new_token"
        assert updated.config["chat_id"] == "new_chat"
        assert updated.id == channel.id