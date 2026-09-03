"""Metrics Page.

Displays charts and visualizations for pipeline metrics.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository


async def render_metrics(
    post_repo: Any,
    setting_repo: Any,
    db_settings: Dict[str, Any],
) -> None:
    """Render the metrics page."""
    st.markdown('<div class="main-header">📈 Metrics</div>',
                unsafe_allow_html=True)

    # Date range selector
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        date_range = st.selectbox(
            "Time Range",
            ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"],
            index=1,
        )
    with col2:
        if date_range == "Custom":
            start_date = st.date_input(
                "Start Date", datetime.now() - timedelta(days=30))
            end_date = st.date_input("End Date", datetime.now())
        else:
            days_map = {"Last 7 days": 7,
                        "Last 30 days": 30, "Last 90 days": 90}
            days = days_map.get(date_range, 30)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Load data
    posts = await _load_posts_data(post_repo, start_date, end_date)

    if not posts:
        st.info("No data available for the selected period")
        return

    df = pd.DataFrame(posts)
    df['date'] = pd.to_datetime(df['created_at']).dt.date

    # Overview metrics
    _render_overview_metrics(df)

    st.divider()

    # Charts in tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Pipeline", "📈 Articles", "🔌 API", "🎯 Deduplication"])

    with tab1:
        _render_pipeline_charts(df)

    with tab2:
        _render_article_charts(df)


async def _load_posts_data(
    post_repo: Any,
    start_date: datetime,
    end_date: datetime,
) -> List[Dict[str, Any]]:
    """Load posts data for metrics."""
    posts = await post_repo.get_recent(days=(end_date - start_date).days, limit=1000)
    return [
        {
            "id": p.id,
            "title": p.title,
            "clean_url": p.clean_url,
            "summary": p.summary,
            "is_duplicate": p.is_duplicate,
            "source_id": p.source_id,
            "channel_id": p.channel_id,
            "template_id": p.template_id,
            "created_at": p.created_at,
        }
        for p in posts
        if start_date <= p.created_at.replace(tzinfo=None) <= end_date
    ]


def _render_overview_metrics(df: pd.DataFrame) -> None:
    """Render overview metric cards."""
    col1, col2, col3, col4, col5 = st.columns(5)

    total_posts = len(df)
    duplicates = df['is_duplicate'].sum(
    ) if 'is_duplicate' in df.columns else 0
    unique_posts = total_posts - duplicates
    channels = df['channel_id'].nunique() if 'channel_id' in df.columns else 0
    sources = df['source_id'].nunique() if 'source_id' in df.columns else 0

    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Posts", total_posts)
        col2.metric("Unique Posts", unique_posts)
        col3.metric("Duplicates", int(duplicates))
        col4.metric("Channels Used", int(channels))
        col5.metric("Sources", int(sources))


def _render_pipeline_charts(df: pd.DataFrame) -> None:
    """Render pipeline performance charts."""
    st.subheader("Pipeline Performance")

    # Posts per day
    daily_counts = df.groupby('date').size().reset_index(name='count')
    fig = px.line(daily_counts, x='date', y='count',
                  title='Posts Published per Day')
    fig.update_layout(xaxis_title="Date", yaxis_title="Posts")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with st.container():
        # Posts by channel
        if 'channel_id' in df.columns:
            channel_counts = df['channel_id'].value_counts().reset_index()
            channel_counts.columns = ['channel_id', 'count']
            fig = px.bar(channel_counts, x='channel_id',
                         y='count', title='Posts by Channel')
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        # Posts by template
        if 'template_id' in df.columns:
            template_counts = df['template_id'].value_counts().reset_index()
            template_counts.columns = ['template_id', 'count']
            fig = px.pie(template_counts, values='count',
                         names='template_id', title='Posts by Template')
            st.plotly_chart(fig, use_container_width=True)


def _render_article_charts(df: pd.DataFrame) -> None:
    """Render article processing charts."""
    st.subheader("Article Processing")

    col1, col2 = st.columns(2)

    with col1:
        # Duplicate vs unique
        if 'is_duplicate' in df.columns:
            dup_counts = df['is_duplicate'].value_counts().reset_index()
            dup_counts.columns = ['is_duplicate', 'count']
            dup_counts['is_duplicate'] = dup_counts['is_duplicate'].map(
                {True: 'Duplicate', False: 'Unique'})
            fig = px.pie(
                dup_counts,
                values='count',
                names='is_duplicate',
                title='Duplicate vs Unique Posts')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Posts by source
        if 'source_id' in df.columns:
            source_counts = df['source_id'].value_counts().reset_index()
            source_counts.columns = ['source_id', 'count']
            fig = px.bar(source_counts, x='source_id',
                         y='count', title='Posts by Source')
            st.plotly_chart(fig, use_container_width=True)


def _render_api_charts() -> None:
    """Render API call metrics charts."""
    st.subheader("API Call Metrics")
    st.info("API metrics require Prometheus integration. Configure Prometheus to scrape metrics endpoint.")


def _render_deduplication_charts(df: pd.DataFrame) -> None:
    """Render deduplication effectiveness charts."""
    st.subheader("Deduplication Effectiveness")

    col1, col2 = st.columns(2)

    with col1:
        if 'is_duplicate' in df.columns:
            dup_rate = df['is_duplicate'].mean() * 100
            st.metric("Overall Duplicate Rate", f"{dup_rate:.1f}%")

    with col2:
        if 'source_id' in df.columns and 'is_duplicate' in df.columns:
            dup_by_source = df.groupby('source_id')[
                'is_duplicate'].mean().reset_index()
            dup_by_source.columns = ['source_id', 'duplicate_rate']
            dup_by_source['duplicate_rate'] = dup_by_source['duplicate_rate'] * 100
            fig = px.bar(
                dup_by_source,
                x='source_id',
                y='duplicate_rate',
                title='Duplicate Rate by Source (%)')
            st.plotly_chart(fig, use_container_width=True)
