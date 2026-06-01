"""create review tables

Revision ID: 0002_create_review_tables
Revises: 0001_create_core_entity_tables
Create Date: 2026-06-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_create_review_tables"
down_revision: Union[str, None] = "0001_create_core_entity_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("spoiler", sa.Boolean(), nullable=False),
        sa.Column("visibility", sa.String(length=20), nullable=False),
        sa.Column("attachment_url", sa.String(length=1000), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("rating >= 0.5 AND rating <= 5.0", name="ck_reviews_rating_range"),
        sa.CheckConstraint(
            "visibility IN ('public', 'followers', 'private')",
            name="ck_reviews_visibility",
        ),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "entity_id", name="uq_reviews_user_entity"),
    )
    op.create_index(op.f("ix_reviews_entity_id"), "reviews", ["entity_id"], unique=False)
    op.create_index(op.f("ix_reviews_id"), "reviews", ["id"], unique=False)
    op.create_index(op.f("ix_reviews_user_id"), "reviews", ["user_id"], unique=False)

    op.create_table(
        "review_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("tag", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_tags_id"), "review_tags", ["id"], unique=False)
    op.create_index(op.f("ix_review_tags_review_id"), "review_tags", ["review_id"], unique=False)
    op.create_index(op.f("ix_review_tags_tag"), "review_tags", ["tag"], unique=False)

    op.create_table(
        "review_edit_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("previous_rating", sa.Float(), nullable=False),
        sa.Column("previous_title", sa.String(length=160), nullable=True),
        sa.Column("previous_body", sa.Text(), nullable=False),
        sa.Column("previous_spoiler", sa.Boolean(), nullable=False),
        sa.Column("previous_visibility", sa.String(length=20), nullable=False),
        sa.Column("previous_attachment_url", sa.String(length=1000), nullable=True),
        sa.Column("edited_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_edit_history_id"), "review_edit_history", ["id"], unique=False)
    op.create_index(
        op.f("ix_review_edit_history_review_id"),
        "review_edit_history",
        ["review_id"],
        unique=False,
    )

    op.create_table(
        "review_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("reporter_user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="ck_review_reports_status",
        ),
        sa.ForeignKeyConstraint(["reporter_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_review_reports_id"), "review_reports", ["id"], unique=False)
    op.create_index(op.f("ix_review_reports_reporter_user_id"), "review_reports", ["reporter_user_id"], unique=False)
    op.create_index(op.f("ix_review_reports_review_id"), "review_reports", ["review_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_review_reports_review_id"), table_name="review_reports")
    op.drop_index(op.f("ix_review_reports_reporter_user_id"), table_name="review_reports")
    op.drop_index(op.f("ix_review_reports_id"), table_name="review_reports")
    op.drop_table("review_reports")

    op.drop_index(op.f("ix_review_edit_history_review_id"), table_name="review_edit_history")
    op.drop_index(op.f("ix_review_edit_history_id"), table_name="review_edit_history")
    op.drop_table("review_edit_history")

    op.drop_index(op.f("ix_review_tags_tag"), table_name="review_tags")
    op.drop_index(op.f("ix_review_tags_review_id"), table_name="review_tags")
    op.drop_index(op.f("ix_review_tags_id"), table_name="review_tags")
    op.drop_table("review_tags")

    op.drop_index(op.f("ix_reviews_user_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_entity_id"), table_name="reviews")
    op.drop_table("reviews")
