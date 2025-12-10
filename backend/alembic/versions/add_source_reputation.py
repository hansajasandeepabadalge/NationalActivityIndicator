"""Add source reputation system tables

Revision ID: add_source_reputation
Revises: layer1_ai_agent_tables
Create Date: 2025-12-08

This migration adds:
- source_reputation: Dynamic source reputation tracking
- source_reputation_history: Historical snapshots for trend analysis
- quality_filter_log: Filtering decision audit log
- reputation_thresholds: Configurable thresholds
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

revision: str = 'add_source_reputation'
down_revision: Union[str, None] = 'layer1_ai_agent_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create source_reputation table
    op.create_table(
        'source_reputation',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('source_name', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('source_type', sa.String(50), default='news'),
        
        # Current Reputation Score
        sa.Column('reputation_score', sa.Float(), default=0.75, nullable=False),
        sa.Column('reputation_tier', sa.String(20), default='silver'),
        
        # Base scores
        sa.Column('initial_credibility', sa.Float(), default=0.75),
        
        # Quality metrics
        sa.Column('avg_quality_score', sa.Float(), default=70.0),
        sa.Column('avg_confidence_score', sa.Float(), default=0.7),
        
        # Accuracy tracking
        sa.Column('accuracy_rate', sa.Float(), default=0.8),
        sa.Column('cross_verification_rate', sa.Float(), default=0.5),
        
        # Volume & consistency
        sa.Column('total_articles', sa.Integer(), default=0),
        sa.Column('articles_last_30_days', sa.Integer(), default=0),
        sa.Column('accepted_articles', sa.Integer(), default=0),
        sa.Column('rejected_articles', sa.Integer(), default=0),
        sa.Column('flagged_articles', sa.Integer(), default=0),
        sa.Column('acceptance_rate', sa.Float(), default=1.0),
        
        # Trend indicators
        sa.Column('is_improving', sa.Boolean(), default=True),
        sa.Column('is_declining', sa.Boolean(), default=False),
        sa.Column('consecutive_quality_days', sa.Integer(), default=0),
        sa.Column('consecutive_poor_days', sa.Integer(), default=0),
        
        # Status & overrides
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_manually_overridden', sa.Boolean(), default=False),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.Column('override_by', sa.String(100), nullable=True),
        sa.Column('override_until', sa.DateTime(), nullable=True),
        
        # Last activity
        sa.Column('last_article_at', sa.DateTime(), nullable=True),
        sa.Column('last_evaluated_at', sa.DateTime(), default=datetime.utcnow),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        
        # Constraints
        sa.CheckConstraint('reputation_score >= 0.0 AND reputation_score <= 1.0', 
                          name='check_reputation_score_range'),
        sa.CheckConstraint('acceptance_rate >= 0.0 AND acceptance_rate <= 1.0',
                          name='check_acceptance_rate_range'),
    )
    
    # Create indexes
    op.create_index('idx_source_reputation_tier', 'source_reputation', ['reputation_tier'])
    op.create_index('idx_source_is_active', 'source_reputation', ['is_active'])
    
    # Create source_reputation_history table
    op.create_table(
        'source_reputation_history',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('source_id', sa.Integer(), sa.ForeignKey('source_reputation.id'), nullable=False, index=True),
        sa.Column('snapshot_date', sa.DateTime(), nullable=False, index=True),
        
        # Snapshot values
        sa.Column('reputation_score', sa.Float(), nullable=False),
        sa.Column('reputation_tier', sa.String(20), nullable=False),
        sa.Column('avg_quality_score', sa.Float(), nullable=False),
        
        # Activity counts
        sa.Column('articles_count', sa.Integer(), default=0),
        sa.Column('accepted_count', sa.Integer(), default=0),
        sa.Column('rejected_count', sa.Integer(), default=0),
        sa.Column('flagged_count', sa.Integer(), default=0),
        
        # Changes
        sa.Column('score_change', sa.Float(), default=0.0),
        sa.Column('tier_changed', sa.Boolean(), default=False),
        sa.Column('acceptance_rate', sa.Float(), default=1.0),
        
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )
    
    op.create_index('idx_reputation_history_source_date', 'source_reputation_history', 
                    ['source_id', 'snapshot_date'])
    
    # Create quality_filter_log table
    op.create_table(
        'quality_filter_log',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('article_id', sa.String(100), nullable=False, index=True),
        sa.Column('source_id', sa.Integer(), sa.ForeignKey('source_reputation.id'), nullable=False, index=True),
        
        # Decision
        sa.Column('action', sa.String(20), nullable=False, index=True),
        sa.Column('action_reason', sa.Text(), nullable=True),
        
        # Scores
        sa.Column('source_reputation_score', sa.Float(), nullable=False),
        sa.Column('article_quality_score', sa.Float(), nullable=True),
        sa.Column('threshold_applied', sa.Float(), nullable=True),
        sa.Column('weight_multiplier', sa.Float(), default=1.0),
        
        # Performance
        sa.Column('filter_latency_ms', sa.Integer(), default=0),
        
        # Review
        sa.Column('reviewed', sa.Boolean(), default=False),
        sa.Column('reviewed_by', sa.String(100), nullable=True),
        sa.Column('review_decision', sa.String(20), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, index=True),
    )
    
    op.create_index('idx_filter_log_action_date', 'quality_filter_log', ['action', 'created_at'])
    
    # Create reputation_thresholds table
    op.create_table(
        'reputation_thresholds',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('threshold_name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('threshold_type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_by', sa.String(100), default='system'),
    )
    
    # Insert default thresholds
    op.execute("""
        INSERT INTO reputation_thresholds (threshold_name, description, value, threshold_type, category, is_active, created_at, updated_at, updated_by)
        VALUES 
        ('MIN_REPUTATION_ACTIVE', 'Minimum reputation score to keep source active', 0.30, 'min', 'reputation', true, NOW(), NOW(), 'system'),
        ('MIN_REPUTATION_TRUSTED', 'Minimum reputation for trusted source status', 0.75, 'min', 'reputation', true, NOW(), NOW(), 'system'),
        ('MIN_ARTICLE_QUALITY', 'Minimum quality score for article acceptance', 40.0, 'min', 'quality', true, NOW(), NOW(), 'system'),
        ('WARNING_QUALITY', 'Quality score triggering warning flag', 60.0, 'target', 'quality', true, NOW(), NOW(), 'system'),
        ('EXCELLENT_QUALITY', 'Quality score for boosted weight', 85.0, 'target', 'quality', true, NOW(), NOW(), 'system'),
        ('MAX_CONSECUTIVE_POOR_DAYS', 'Days of poor performance before auto-disable', 7.0, 'max', 'reputation', true, NOW(), NOW(), 'system'),
        ('REPUTATION_DECAY_RATE', 'Daily decay rate for reputation (no activity)', 0.001, 'target', 'reputation', true, NOW(), NOW(), 'system'),
        ('REPUTATION_BOOST_RATE', 'Boost rate for quality articles', 0.01, 'target', 'reputation', true, NOW(), NOW(), 'system'),
        ('REPUTATION_PENALTY_RATE', 'Penalty rate for poor quality articles', 0.02, 'target', 'reputation', true, NOW(), NOW(), 'system')
    """)


def downgrade() -> None:
    op.drop_table('quality_filter_log')
    op.drop_table('source_reputation_history')
    op.drop_table('reputation_thresholds')
    op.drop_table('source_reputation')
