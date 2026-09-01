"""Logs Page.

Displays searchable and filterable application logs.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

try:
    import plotly.express as px
except ImportError:
    px = None

from infrastructure.db.repositories.log_repo import SqlAlchemyLogRepository, LogFilters, Pagination


async def render_logs(
    log_repo: Any,
    db_settings: Dict[str, Any],
) -> None:
    """Render the logs page."""
    st.markdown('<div class="main-header">📋 Logs</div>', unsafe_allow_html=True)
    
    # Initialize session state for logs
    if "logs_page" not in st.session_state:
        st.session_state.logs_page = 1
    if "logs_filters" not in st.session_state:
        st.session_state.logs_filters = {}
    if "logs_auto_refresh" not in st.session_state:
        st.session_state.logs_auto_refresh = False
    if "logs_refresh_interval" not in st.session_state:
        st.session_state.logs_refresh_interval = 30
    
    # Auto-refresh
    if st.session_state.logs_auto_refresh:
        st_autorefresh(interval=st.session_state.logs_refresh_interval * 1000, key="logs_autorefresh")
    
    # Filters
    _render_log_filters()
    
    st.divider()
    
    # Load and display logs
    await _render_logs_table(log_repo)
    
def _render_log_filters() -> None:
    """Render log filter controls."""
    st.subheader("🔍 Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        level = st.selectbox(
            "Level",
            ["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            index=0,
            key="log_filter_level",
        )
    
    with col2:
        module = st.text_input("Module", placeholder="e.g. pipeline.steps.fetch_rss", key="log_filter_module")
    
    with col3:
        correlation_id = st.text_input("Correlation ID", placeholder="e.g. a1b2c3d4", key="log_filter_correlation")
    
    with col4:
        search = st.text_input("Search", placeholder="Search in message...", key="log_filter_search")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        start_date = st.date_input(
            "From",
            datetime.now() - timedelta(days=7),
            key="log_filter_start",
        )
    with col2:
        end_date = st.date_input(
            "To",
            datetime.now(),
            key="log_filter_end",
        )
    with col3:
        page_size = st.selectbox(
            "Page Size",
            [25, 50, 100, 200],
            index=1,
            key="log_page_size",
        )
    with col4:
        auto_refresh = st.checkbox(
            "Auto-refresh",
            value=st.session_state.logs_auto_refresh,
            key="log_auto_refresh",
        )
        if auto_refresh:
            interval = st.selectbox(
                "Interval (s)",
                [10, 30, 60, 300],
                index=1,
                key="log_refresh_interval",
            )
            st.session_state.logs_refresh_interval = interval
    
    # Update filters in session state
    st.session_state.logs_filters = {
        "level": level if level != "All" else None,
        "module": module or None,
        "correlation_id": correlation_id or None,
        "search_query": search or None,
        "start_time": datetime.combine(start_date, datetime.min.time()) if start_date else None,
        "end_time": datetime.combine(end_date, datetime.max.time()) if end_date else None,
    }

async def _render_logs_table(log_repo: Any) -> None:
    """Render the logs table with pagination."""
    st.subheader("📋 Log Entries")
    
    # Get pagination
    page = st.session_state.get("logs_page", 1)
    page_size = st.session_state.get("log_page_size", 50)
    
    # Build filters
    filters = st.session_state.get("logs_filters", {})
    log_filters = LogFilters(
        level=filters.get("level"),
        module=filters.get("module"),
        start_time=filters.get("start_time"),
        end_time=filters.get("end_time"),
        correlation_id=filters.get("correlation_id"),
        search_query=filters.get("search_query"),
    )
    pagination = Pagination(page=page, page_size=page_size)
    
    # Load logs
    logs = await log_repo.get_logs(filters=log_filters, pagination=pagination)
    total_count = await log_repo.count_logs(filters=LogFilters(**{k: v for k, v in filters.items() if k != "page"}))
    
    if not logs:
        st.info("No logs found matching the filters")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame([
        {
            "Time": log.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "Level": log.level,
            "Module": log.module,
            "Message": log.message[:100] + "..." if len(log.message) > 100 else log.message,
            "Correlation ID": log.context_json.get("correlation_id", "") if log.context_json else "",
        }
        for log in logs
    ])
    
    # Display table with selection
    selected_rows = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Time": st.column_config.TextColumn("Time", width="medium"),
            "Level": st.column_config.TextColumn("Level", width="small"),
            "Module": st.column_config.TextColumn("Module", width="medium"),
            "Message": st.column_config.TextColumn("Message", width="large"),
            "Correlation ID": st.column_config.TextColumn("Correlation ID", width="small"),
        },
        on_select="rerun",
        selection_mode="single-row",
    )
    
    # Show log detail if row selected
    if selected_rows.selection.rows:
        selected_idx = selected_rows.selection.rows[0]
        selected_log = logs[selected_idx]
        _render_log_detail(selected_log)
    
    # Pagination
    total_pages = (total_count + page_size - 1) // page_size
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=page <= 1, use_container_width=True):
                st.session_state.logs_page = page - 1
                st.rerun()
        with col2:
            st.markdown(f"<div style='text-align: center'>Page {page} of {total_pages} ({total_count} total)</div>", unsafe_allow_html=True)
        with col3:
            if st.button("Next ➡️", disabled=page >= total_pages, use_container_width=True):
                st.session_state.logs_page = page + 1
                st.rerun()


def _render_log_detail(log: Any) -> None:
    """Render detailed log view in an expander."""
    with st.expander("📄 Log Detail", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Time:** {log.timestamp}")
            st.write(f"**Level:** {log.level}")
            st.write(f"**Module:** {log.module}")
        with col2:
            st.write(f"**Correlation ID:** {log.context_json.get('correlation_id', 'N/A') if log.context_json else 'N/A'}")
            st.write(f"**User ID:** {log.user_id or 'N/A'}")
        
        st.write("**Message:**")
        st.code(log.message, language="text")
        
        if log.context_json:
            st.write("**Context:**")
            st.json(log.context_json)


async def _render_log_stats(log_repo: Any) -> None:
    """Render log statistics."""
    st.subheader("📊 Log Statistics")
    
    # Get stats for last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    stats = await log_repo.get_log_stats(start_time=start_time, end_time=end_time)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Logs (24h)", stats.get("total", 0))
    with col2:
        by_level = stats.get("by_level", {})
        error_count = by_level.get("ERROR", 0) + by_level.get("CRITICAL", 0)
        st.metric("Errors (24h)", error_count, delta_color="inverse")
    with col3:
        st.metric("Modules (24h)", len(stats.get("by_module", {})))
    
    # By level chart
    by_level = stats.get("by_level", {})
    if by_level:
        st.subheader("Logs by Level (24h)")
        level_df = pd.DataFrame(list(by_level.items()), columns=["Level", "Count"])
        fig = px.bar(level_df, x="Level", y="Count", color="Level", title="Logs by Level (24h)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Top modules
    by_module = stats.get("by_module", {})
    if by_module:
        st.subheader("Top Modules (24h)")
        module_df = pd.DataFrame(list(by_module.items()), columns=["Module", "Count"])
        fig = px.bar(module_df, x="Module", y="Count", title="Top Modules by Log Count")
        st.plotly_chart(fig, use_container_width=True)
    st.divider()
    
    # Log statistics
    _render_log_stats(log_repo)