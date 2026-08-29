"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-08-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # rss_sources
    op.create_table(
        'rss_sources',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('last_fetch', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url', name='uq_rss_sources_url'),
    )
    op.create_index('ix_rss_sources_enabled', 'rss_sources', ['enabled'], postgresql_where=sa.text('enabled = true'))

    # channels
    op.create_table(
        'channels',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_channels_name'),
    )
    op.create_index('ix_channels_type_enabled', 'channels', ['type', 'enabled'], postgresql_where=sa.text('enabled = true'))

    # llm_models
    op.create_table(
        'llm_models',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('provider', sa.String(30), nullable=False),
        sa.Column('model_id', sa.String(100), nullable=False),
        sa.Column('api_key_ref', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_llm_models_name'),
    )
    op.create_index('ix_llm_models_provider_active', 'llm_models', ['provider', 'is_active'], postgresql_where=sa.text('is_active = true'))

    # settings
    op.create_table(
# published_posts
    op.create_table(
        'published_posts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('clean_url', sa.String(500), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('embedding', postgresql.VECTOR(768), nullable=False),
        sa.Column('is_duplicate', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('source_id', sa.BigInteger(), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), nullable=True),
        sa.Column('llm_model_id', sa.BigInteger(), nullable=True),
        sa.Column('template_id', sa.String(50), nullable=True),
        sa.Column('post_text', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clean_url', name='uq_published_posts_clean_url'),
        sa.ForeignKeyConstraint(['source_id'], ['rss_sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['llm_model_id'], ['llm_models.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_published_posts_created_at', 'published_posts', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    op.create_index('ix_published_posts_is_duplicate', 'published_posts', ['is_duplicate'], postgresql_where=sa.text('is_duplicate = false'))

    # users
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='admin'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username', name='uq_users_username'),
    )

    # logs
    op.create_table(
        'logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('level', sa.String(10), nullable=False),
        sa.Column('module', sa.String(100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('context_json', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_logs_timestamp', 'logs', ['timestamp'], postgresql_using='btree', postgresql_ops={'timestamp': 'DESC'})
    op.create_index('ix_logs_level', 'logs', ['level'])
    op.create_index('ix_logs_module', 'logs', ['module'])


def downgrade() -> None:
    op.drop_table('logs')
    op.drop_table('users')
    op.drop_table('published_posts')
    op.drop_table('settings')
    op.drop_table('llm_models')
    op.drop_table('channels')
    op.drop_table('rss_sources')
        'settings',
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('key'),
    )