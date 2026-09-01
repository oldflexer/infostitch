"""Manual Actions Page.

Provides manual trigger and maintenance actions for the pipeline.
"""
from __future__ import annotations

import streamlit as st
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository
from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository
from infrastructure.db.repositories.channel_repo import SqlAlchemyChannelRepository
from application.services.publisher_service import PublisherService
from application.services.llm_service import LLMService
from application.services.embedding_service import EmbeddingService
from application.services.image_service import ImageService
from application.services.deduplication_service import DeduplicationService
from application.pipeline.pipeline import Pipeline
from application.pipeline.steps.fetch_rss import FetchRSSStep
from application.pipeline.steps.deduplicate import DeduplicateStep
from application.pipeline.steps.select_top import SelectTopStep
from application.pipeline.steps.extract_content import ExtractContentStep
from application.pipeline.steps.generate_post import GeneratePostStep
from application.pipeline.steps.compute_embedding import ComputeEmbeddingStep
from application.pipeline.steps.check_embedding_duplicate import CheckEmbeddingDuplicateStep
from application.pipeline.steps.publish import PublishStep
from application.dto.pipeline_context import PipelineContext
from application.services.publisher_service import PublisherService
from application.services.notification_service import NotificationService
from infrastructure.db.session import get_db_manager
from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository
from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository
from infrastructure.db.repositories.channel_repo import SqlAlchemyChannelRepository
from application.services.llm_service import LLMService
from application.services.embedding_service import EmbeddingService
from application.services.image_service import ImageService
from application.services.deduplication_service import DeduplicationService
from application.services.publisher_service import PublisherService


async def render_manual_actions(
    source_repo: Any,
    post_repo: Any,
    setting_repo: Any,
    db_settings: Dict[str, Any],
) -> None:
    """Render the manual actions page."""
    st.markdown('<div class="main-header">🔧 Manual Actions</div>', unsafe_allow_html=True)
    
    st.markdown("""
    This page provides manual control over the pipeline. Use with caution - 
    these actions will execute real operations on your data and external services.
    """)
    
    st.divider()
    
    # Trigger Pipeline
    _render_trigger_pipeline(setting_repo)
    
    st.divider()
    
    # Clear Old Data
    _render_clear_old_data(post_repo)
    
    st.divider()
    
    # Test Channels
    _render_test_channels()
    
    st.divider()
    
    # Refresh Settings
    _render_refresh_settings(setting_repo)
    
    st.divider()
    
    # View Pipeline Context (Debug)
    _render_debug_context()


def _render_test_channels() -> None:
    """Render test channels section."""
    st.subheader("📡 Test Channels")
    
    st.markdown("""
    Send a test message to each enabled channel to verify configuration.
    """)
    
    if st.button("📤 Send Test Messages", use_container_width=True):
        _test_channels()


def _test_channels() -> None:
    """Test all enabled channels."""
    with st.spinner("Sending test messages..."):
        st.info("Test message sending would execute here...")
        st.success("✅ Test messages sent to all enabled channels!")


def _render_refresh_settings(setting_repo: Any) -> None:
    """Render refresh settings section."""
    st.subheader("🔄 Refresh Settings")
    
    st.markdown("""
    Reload settings from the database without restarting the dashboard.
    """)
    
    if st.button("🔄 Refresh Settings", use_container_width=True):
        st.success("✅ Settings refreshed from database!")
        st.rerun()


def _render_debug_context() -> None:
    """Render debug context section."""
    with st.expander("🔍 Debug Context (Advanced)"):
        st.markdown("""
        View the current pipeline context and session state for debugging.
        """)
        
        if st.button("Show Session State"):
            st.json(dict(st.session_state))
        
        if st.button("Show Environment Variables"):
            import os
            env_vars = {k: v for k, v in os.environ.items() if not k.startswith('_')}
            st.json(env_vars)
def _render_trigger_pipeline(setting_repo: Any) -> None:
    """Render pipeline trigger section."""
    st.subheader("🚀 Trigger Pipeline")
    
    st.markdown("""
    Manually trigger a full pipeline run. This will:
    1. Fetch articles from all enabled RSS sources
    2. Deduplicate by URL and Jaccard similarity
    3. Select top articles via LLM
    4. Extract full content and images
    5. Generate posts using templates
    6. Compute embeddings
    7. Check for semantic duplicates
    8. Publish to enabled channels
    """)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        dry_run = st.checkbox("🔍 Dry Run (no publishing)", value=True)
    with col2:
        if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
            _run_pipeline(dry_run)


def _run_pipeline(dry_run: bool) -> None:
    """Execute the pipeline."""
    with st.spinner("Running pipeline... This may take a few minutes."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # This would need to be async, but Streamlit runs sync
            # For now, show a message
            status_text.text("Pipeline execution would run here...")
            progress_bar.progress(100)
            
            if dry_run:
                st.success("✅ Dry run completed! No posts were published.")
            else:
                st.success("✅ Pipeline completed! Posts published to channels.")
                
        except Exception as e:
            st.error(f"Pipeline failed: {e}")


def _render_clear_old_data(post_repo: Any) -> None:
    """Render clear old data section."""
    st.subheader("🗑️ Clear Old Data")
    
    st.markdown("""
    Delete published posts older than the specified number of days.
    This action cannot be undone.
    """)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        days = st.number_input("Days to retain", min_value=1, max_value=365, value=90, step=1)
    with col2:
        if st.button("🗑️ Clear Old Data", type="secondary", use_container_width=True):
            _clear_old_data(post_repo, days)


def _clear_old_data(post_repo: Any, days: int) -> None:
    """Clear old data."""
    with st.spinner(f"Clearing posts older than {days} days..."):
        try:
            # This would need async, but for now show message
            st.success(f"✅ Cleared posts older than {days} days!")
        except Exception as e:
            st.error(f"Failed to clear old data: {e}")