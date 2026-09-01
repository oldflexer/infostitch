"""Main Streamlit Dashboard Application.

Provides admin UI for monitoring and configuring the InfoStitch pipeline.
"""
from __future__ import annotations

import streamlit as st
import asyncio
from typing import Optional

from infrastructure.config import get_settings
from infrastructure.db.session import get_db_manager, init_db
from infrastructure.db.repositories.user_repo import SqlAlchemyUserRepository
from infrastructure.db.repositories.source_repo import SqlAlchemySourceRepository
from infrastructure.db.repositories.channel_repo import SqlAlchemyChannelRepository
from infrastructure.db.repositories.llm_model_repo import SqlAlchemyLLMModelRepository
from infrastructure.db.repositories.setting_repo import SqlAlchemySettingRepository
from infrastructure.db.repositories.post_repo import SqlAlchemyPostRepository
from infrastructure.db.repositories.log_repo import SqlAlchemyLogRepository
from presentation.dashboard.pages.overview import render_overview
from presentation.dashboard.pages.logs import render_logs
from presentation.dashboard.pages.settings import render_settings
from presentation.dashboard.pages.metrics import render_metrics
from presentation.dashboard.pages.manual_actions import render_manual_actions
async def initialize_database() -> None:
    """Initialize database connection."""
    if not st.session_state.db_initialized:
        await init_db()
        st.session_state.db_initialized = True


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


async def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user credentials."""
    db_manager = get_db_manager()
    async with db_manager.session() as session:
        user_repo = SqlAlchemyUserRepository(session)
        user = await user_repo.get_by_username(username)
        if user and verify_password(password, user.password_hash):
            return {"id": user.id, "username": user.username, "role": user.role}
    return None


def login_form() -> None:
    """Render login form."""
    st.markdown('<div class="main-header">📰 InfoStitch Dashboard</div>', unsafe_allow_html=True)
    st.markdown("Please log in to access the dashboard.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if username and password:
                user = asyncio.run(authenticate_user(username, password))
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")


def logout() -> None:
    """Log out current user."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()


def render_sidebar() -> None:
    """Render sidebar navigation."""
    with st.sidebar:
        st.markdown(f"**Logged in as:** {st.session_state.user['username']} ({st.session_state.user['role']})")
        st.divider()
        
        # Navigation
        pages = {
            "📊 Overview": "overview",
            "📈 Metrics": "metrics",
            "📋 Logs": "logs",
            "⚙️ Settings": "settings",
            "🔧 Manual Actions": "manual_actions",
        }
        
        selected_page = st.radio(
            "Navigation",
            options=list(pages.keys()),
            format_func=lambda x: x,
            key="navigation",
        )
        
        st.session_state.current_page = pages[selected_page]
        
        st.divider()
        
        # User info
        st.caption(f"Role: {st.session_state.user['role']}")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()

# Page configuration
st.set_page_config(
    page_title="InfoStitch Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-success { color: #28a745; font-weight: bold; }
    .status-error { color: #dc3545; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-info { color: #17a2b8; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)


async def render_page_content() -> None:
    """Render the selected page content."""
    page = st.session_state.get("current_page", "overview")
    
    # Initialize database
    await initialize_database()
    
    # Get database session
    db_manager = get_db_manager()
    async with db_manager.session() as session:
        # Initialize repositories
        source_repo = SqlAlchemySourceRepository(session)
        channel_repo = SqlAlchemyChannelRepository(session)
        llm_model_repo = SqlAlchemyLLMModelRepository(session)
        setting_repo = SqlAlchemySettingRepository(session)
        post_repo = SqlAlchemyPostRepository(session)
        log_repo = SqlAlchemyLogRepository(session)
        
        # Load settings
        db_settings = await setting_repo.get_all()
        
        # Render selected page
        if page == "overview":
            await render_overview(
                source_repo=source_repo,
                channel_repo=channel_repo,
                post_repo=post_repo,
                setting_repo=setting_repo,
                db_settings=db_settings,
            )
        elif page == "metrics":
            await render_metrics(
                post_repo=post_repo,
                setting_repo=setting_repo,
                db_settings=db_settings,
            )
        elif page == "logs":
            await render_logs(
                log_repo=log_repo,
                db_settings=db_settings,
            )
        elif page == "settings":
            await render_settings(
                source_repo=source_repo,
                channel_repo=channel_repo,
                llm_model_repo=llm_model_repo,
                setting_repo=setting_repo,
                db_settings=db_settings,
            )
        elif page == "manual_actions":
            await render_manual_actions(
                source_repo=source_repo,
                post_repo=post_repo,
                setting_repo=setting_repo,
                db_settings=db_settings,
            )


def init_session_state() -> None:
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False


def main() -> None:
    """Main dashboard entry point."""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_form()
    else:
        render_sidebar()
        asyncio.run(render_page_content())


if __name__ == "__main__":
    main()


def init_session_state() -> None:
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False