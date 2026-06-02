"""create community post tables

Revision ID: 0006_create_post_tables
Revises: 0005_create_community_tables
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_create_post_tables"
down_revision: Union[str, None] = "0005_create_community_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "community_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("community_id", sa.Integer(), nullable=False),
        sa.Column("author_user_id", sa.Integer(), nullable=False),
        sa.Column("post_type", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("media_url", sa.String(length=1000), nullable=True),
        sa.Column("spoiler", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "post_type IN ('review', 'hot_take', 'poll', 'meme_edit', 'fan_theory', "
            "'reaction', 'ranking', 'cover_clip', 'discussion')",
            name="ck_community_posts_post_type",
        ),
        sa.CheckConstraint(
            "status IN ('published', 'hidden', 'removed')",
            name="ck_community_posts_status",
        ),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["community_id"], ["communities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_community_posts_author_user_id"), "community_posts", ["author_user_id"], unique=False)
    op.create_index(op.f("ix_community_posts_community_id"), "community_posts", ["community_id"], unique=False)
    op.create_index(op.f("ix_community_posts_id"), "community_posts", ["id"], unique=False)
    op.create_index(op.f("ix_community_posts_post_type"), "community_posts", ["post_type"], unique=False)
    op.create_index(op.f("ix_community_posts_status"), "community_posts", ["status"], unique=False)

    op.create_table(
        "community_blocked_words",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("community_id", sa.Integer(), nullable=False),
        sa.Column("word", sa.String(length=120), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["community_id"], ["communities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("community_id", "word", name="uq_community_blocked_words_word"),
    )
    op.create_index(
        op.f("ix_community_blocked_words_community_id"),
        "community_blocked_words",
        ["community_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_community_blocked_words_created_by_user_id"),
        "community_blocked_words",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(op.f("ix_community_blocked_words_id"), "community_blocked_words", ["id"], unique=False)

    op.create_table(
        "post_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("reporter_user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="ck_post_reports_status",
        ),
        sa.ForeignKeyConstraint(["post_id"], ["community_posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reporter_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_reports_id"), "post_reports", ["id"], unique=False)
    op.create_index(op.f("ix_post_reports_post_id"), "post_reports", ["post_id"], unique=False)
    op.create_index(op.f("ix_post_reports_reporter_user_id"), "post_reports", ["reporter_user_id"], unique=False)

    op.create_table(
        "post_moderation_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("moderator_user_id", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "action_type IN ('hide', 'unhide', 'remove', 'restore')",
            name="ck_post_moderation_actions_action_type",
        ),
        sa.ForeignKeyConstraint(["moderator_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["community_posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_moderation_actions_id"), "post_moderation_actions", ["id"], unique=False)
    op.create_index(
        op.f("ix_post_moderation_actions_moderator_user_id"),
        "post_moderation_actions",
        ["moderator_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_post_moderation_actions_post_id"),
        "post_moderation_actions",
        ["post_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_post_moderation_actions_post_id"), table_name="post_moderation_actions")
    op.drop_index(op.f("ix_post_moderation_actions_moderator_user_id"), table_name="post_moderation_actions")
    op.drop_index(op.f("ix_post_moderation_actions_id"), table_name="post_moderation_actions")
    op.drop_table("post_moderation_actions")

    op.drop_index(op.f("ix_post_reports_reporter_user_id"), table_name="post_reports")
    op.drop_index(op.f("ix_post_reports_post_id"), table_name="post_reports")
    op.drop_index(op.f("ix_post_reports_id"), table_name="post_reports")
    op.drop_table("post_reports")

    op.drop_index(op.f("ix_community_blocked_words_id"), table_name="community_blocked_words")
    op.drop_index(
        op.f("ix_community_blocked_words_created_by_user_id"),
        table_name="community_blocked_words",
    )
    op.drop_index(op.f("ix_community_blocked_words_community_id"), table_name="community_blocked_words")
    op.drop_table("community_blocked_words")

    op.drop_index(op.f("ix_community_posts_status"), table_name="community_posts")
    op.drop_index(op.f("ix_community_posts_post_type"), table_name="community_posts")
    op.drop_index(op.f("ix_community_posts_id"), table_name="community_posts")
    op.drop_index(op.f("ix_community_posts_community_id"), table_name="community_posts")
    op.drop_index(op.f("ix_community_posts_author_user_id"), table_name="community_posts")
    op.drop_table("community_posts")
