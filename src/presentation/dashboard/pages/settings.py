"""Settings Page.

Provides CRUD interface for RSS sources, channels, LLM models, and thresholds.
"""
from __future__ import annotations

import streamlit as st
import json
from typing import Any, Dict, List, Optional

from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository
from infrastructure.db.repositories.channel_repo import SqlAlchemyChannelRepository
from infrastructure.db.repositories.llm_model_repo import SqlAlchemyLLMModelRepository
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository


async def render_settings(
    source_repo: Any,
    channel_repo: Any,
    llm_model_repo: Any,
    setting_repo: Any,
    db_settings: Dict[str, Any],
) -> None:
    """Render the settings page."""
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📡 RSS Sources",
        "📡 Channels",
        "🤖 LLM Models",
        "🎯 Thresholds",
        "📝 Templates",
    ])
    
    with tab1:
        await _render_rss_sources_tab(source_repo)
    
    with tab2:
        await _render_channels_tab(channel_repo)
    
    with tab3:
        await _render_llm_models_tab(llm_model_repo)
    
async def _render_rss_sources_tab(source_repo: Any) -> None:
    """Render RSS sources management tab."""
    st.subheader("📡 RSS Sources")
    
    # Add new source
    with st.expander("➕ Add New RSS Source", expanded=False):
        with st.form("add_rss_source"):
            url = st.text_input("RSS URL", placeholder="https://example.com/feed.xml")
            enabled = st.checkbox("Enabled", value=True)
            submitted = st.form_submit_button("Add Source")
            if submitted and url:
                await source_repo.add(url=url, enabled=enabled)
                st.success("RSS source added!")
                st.rerun()
    
    # List sources
    sources = await source_repo.get_all()
    
    if not sources:
        st.info("No RSS sources configured")
        return
    
    for source in sources:
        with st.container():
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            with col1:
                st.write(f"**{source.url}**")
                st.caption(f"Created: {source.created_at.strftime('%Y-%m-%d')}")
            with col2:
                status = "🟢 Enabled" if source.enabled else "🔴 Disabled"
                st.write(status)
            with col3:
                if st.button("🔄 Toggle", key=f"toggle_source_{source.id}", use_container_width=True):
                    updated = source.toggle_enabled()
                    await source_repo.update(updated)
                    st.rerun()
            with col4:
                if st.button("🗑️ Delete", key=f"delete_source_{source.id}", use_container_width=True, type="secondary"):
                    await source_repo.delete(source.id)
                    st.success("Source deleted!")
                    st.rerun()
        st.divider()


async def _render_channels_tab(channel_repo: Any) -> None:
    """Render channels management tab."""
    st.subheader("📡 Channels")
    
    # Add new channel
    with st.expander("➕ Add New Channel", expanded=False):
        with st.form("add_channel"):
            name = st.text_input("Name", placeholder="Telegram Channel")
            type_ = st.selectbox("Type", ["telegram", "vk", "max"])
            enabled = st.checkbox("Enabled", value=True)
            
            st.write("**Configuration (JSON)**")
            config = st.text_area(
                "Config",
                value=json.dumps({
                    "chat_id": "",
                    "bot_token_ref": "",
                }, indent=2),
                height=150,
            )
            submitted = st.form_submit_button("Add Channel")
            if submitted and name:
                try:
                    config_dict = json.loads(config)
                    await channel_repo.add(name=name, type=type_, enabled=enabled, config=config_dict)
                    st.success("Channel added!")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON configuration")
    
    # List channels
    channels = await channel_repo.get_all()
    
    if not channels:
        st.info("No channels configured")
        return
    
    for channel in channels:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"**{channel.name}** ({channel.type})")
                st.caption(f"Created: {channel.created_at.strftime('%Y-%m-%d')}")
            with col2:
                status = "🟢 Enabled" if channel.enabled else "🔴 Disabled"
                st.write(status)
            with col3:
                if st.button("✏️ Edit", key=f"edit_channel_{channel.id}", use_container_width=True):
                    st.session_state[f"edit_channel_{channel.id}"] = True
                    st.rerun()
            with col4:
                if st.button("🗑️ Delete", key=f"delete_channel_{channel.id}", use_container_width=True, type="secondary"):
                    await channel_repo.delete(channel.id)
                    st.success("Channel deleted!")
                    st.rerun()
            
            # Edit form
            if st.session_state.get(f"edit_channel_{channel.id}", False):
                with st.form(f"edit_channel_form_{channel.id}"):
                    new_name = st.text_input("Name", value=channel.name)
                    new_type = st.selectbox("Type", ["telegram", "vk", "max"], index=["telegram", "vk", "max"].index(channel.type))
                    new_enabled = st.checkbox("Enabled", value=channel.enabled)
                    new_config = st.text_area("Config (JSON)", value=json.dumps(channel.config, indent=2), height=150)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save", use_container_width=True):
                            try:
                                config_dict = json.loads(new_config)
                                updated = channel.update_config(config_dict)
                                updated = updated.toggle_enabled() if updated.enabled != new_enabled else updated
                                updated = updated.update_config(config_dict)
                                await channel_repo.update(updated)
                                st.session_state[f"edit_channel_{channel.id}"] = False
                                st.success("Channel updated!")
                                st.rerun()
                            except json.JSONDecodeError:
                                st.error("Invalid JSON configuration")
                    with col2:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.session_state[f"edit_channel_{channel.id}"] = False
async def _render_llm_models_tab(llm_model_repo: Any) -> None:
    """Render LLM models management tab."""
    st.subheader("🤖 LLM Models")
    
    # Add new model
    with st.expander("➕ Add New LLM Model", expanded=False):
        with st.form("add_llm_model"):
            name = st.text_input("Name", placeholder="gemini-1.5-flash")
            provider = st.selectbox("Provider", ["gemini", "openai", "anthropic", "custom"])
            model_id = st.text_input("Model ID", placeholder="gemini-1.5-flash-latest")
            api_key_ref = st.text_input("API Key Ref (env var name)", placeholder="GEMINI_API_KEY")
            is_active = st.checkbox("Active", value=True)
            submitted = st.form_submit_button("Add Model")
            if submitted and name:
                await llm_model_repo.add(
                    name=name,
                    provider=provider,
                    model_id=model_id,
                    api_key_ref=api_key_ref,
                    is_active=is_active,
                )
                st.success("LLM model added!")
                st.rerun()
    
    # List models
    models = await llm_model_repo.get_all()
    
    if not models:
        st.info("No LLM models configured")
        return
    
    for model in models:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"**{model.name}** ({model.provider})")
                st.caption(f"Model: {model.model_id}")
            with col2:
                status = "🟢 Active" if model.is_active else "🔴 Inactive"
                st.write(status)
            with col3:
                if st.button("🔄 Toggle", key=f"toggle_model_{model.id}", use_container_width=True):
                    updated = model.toggle_active()
                    await llm_model_repo.update(updated)
                    st.rerun()
            with col4:
                if st.button("🗑️ Delete", key=f"delete_model_{model.id}", use_container_width=True, type="secondary"):
                    await llm_model_repo.delete(model.id)
                    st.success("Model deleted!")
                    st.rerun()
        st.divider()


async def _render_thresholds_tab(setting_repo: Any, db_settings: Dict[str, Any]) -> None:
    """Render thresholds configuration tab."""
    st.subheader("🎯 Thresholds & Limits")
    
    # Editable thresholds
    thresholds = {
        "jaccard_threshold": ("Jaccard Similarity Threshold", "float", 0.0, 1.0),
        "embedding_similarity_threshold": ("Embedding Similarity Threshold", "float", 0.0, 1.0),
        "post_length_min": ("Min Post Length", "int", 100, 2000),
        "post_length_max": ("Max Post Length", "int", 100, 2000),
        "post_total_max_length": ("Total Max Length", "int", 100, 5000),
        "dedup_window_days_stage1": ("Stage 1 Dedup Window (days)", "int", 1, 30),
        "dedup_window_days_stage2": ("Stage 2 Dedup Window (days)", "int", 1, 30),
        "cleanup_retention_days": ("Cleanup Retention (days)", "int", 1, 365),
        "pipeline_interval_hours": ("Pipeline Interval (hours)", "int", 1, 24),
        "max_articles_per_run": ("Max Articles Per Run", "int", 1, 100),
    }
    
    with st.form("thresholds_form"):
        for key, (label, type_, min_val, max_val) in thresholds.items():
            current = db_settings.get(key, "")
            if type_ == "float":
                st.number_input(label, value=float(current), min_value=min_val, max_value=max_val, step=0.01, key=f"setting_{key}")
            else:
                st.number_input(label, value=int(current), min_value=min_val, max_value=max_val, step=1, key=f"setting_{key}")
        
        if st.form_submit_button("Save Thresholds"):
            for key in thresholds:
                await setting_repo.set(key, str(st.session_state[f"setting_{key}"]))
            st.success("Thresholds saved!")
            st.rerun()


async def _render_templates_tab(setting_repo: Any, db_settings: Dict[str, Any]) -> None:
    """Render templates configuration tab."""
    st.subheader("📝 Templates")
    
    # Template pool
    current_pool = db_settings.get("template_pool", "[]")
    try:
        pool = json.loads(current_pool)
    except:
        pool = []
    
    with st.form("templates_form"):
        st.write("**Template Pool (JSON Array)**")
        pool_json = st.text_area(
            "Template Pool",
            value=json.dumps(pool, indent=2),
            height=200,
            key="template_pool_json",
        )
        
        st.write("**Default Template ID**")
        default_template = st.text_input(
            "Default Template",
            value=db_settings.get("default_template_id", "news_brief"),
            key="default_template_id",
        )
        
        if st.form_submit_button("Save Templates"):
            try:
                pool_parsed = json.loads(st.session_state.template_pool_json)
                await setting_repo.set("template_pool", json.dumps(pool_parsed))
                await setting_repo.set("default_template_id", st.session_state.default_template_id)
                st.success("Templates saved!")
                st.rerun()
            except json.JSONDecodeError:
                st.error("Invalid JSON in template pool")
        st.divider()
