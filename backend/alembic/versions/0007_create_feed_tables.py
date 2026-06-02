"""create feed tables

Revision ID: 0007_create_feed_tables
Revises: 0006_create_post_tables
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_create_feed_tables"
down_revision: Union[str, None] = "0006_create_post_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "feed_regions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_feed_regions_code"), "feed_regions", ["code"], unique=False)
    op.create_index(op.f("ix_feed_regions_id"), "feed_regions", ["id"], unique=False)

    op.create_table(
        "feed_cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("subtitle", sa.String(length=255), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("card_type", sa.String(length=40), server_default="spotlight", nullable=False),
        sa.Column("status", sa.String(length=30), server_default="draft", nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("source_type", sa.String(length=40), server_default="admin_created", nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("region", sa.String(length=20), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("approved_by_user_id", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "card_type IN ('trending_entity', 'new_release', 'trailer_drop', 'top_chart', "
            "'spotlight', 'official_update', 'recommendation', 'announcement')",
            name="ck_feed_cards_card_type",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'pending_review', 'approved', 'rejected', 'published', 'archived')",
            name="ck_feed_cards_status",
        ),
        sa.CheckConstraint(
            "source_type IN ('admin_created', 'system_suggested', 'external_ingestion')",
            name="ck_feed_cards_source_type",
        ),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["region"], ["feed_regions.code"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feed_cards_approved_by_user_id"), "feed_cards", ["approved_by_user_id"], unique=False)
    op.create_index(op.f("ix_feed_cards_card_type"), "feed_cards", ["card_type"], unique=False)
    op.create_index(op.f("ix_feed_cards_created_by_user_id"), "feed_cards", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_feed_cards_id"), "feed_cards", ["id"], unique=False)
    op.create_index(op.f("ix_feed_cards_region"), "feed_cards", ["region"], unique=False)
    op.create_index(op.f("ix_feed_cards_status"), "feed_cards", ["status"], unique=False)

    op.create_table(
        "feed_card_entities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("feed_card_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["feed_card_id"], ["feed_cards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("feed_card_id", "entity_id", name="uq_feed_card_entities_card_entity"),
    )
    op.create_index(op.f("ix_feed_card_entities_entity_id"), "feed_card_entities", ["entity_id"], unique=False)
    op.create_index(op.f("ix_feed_card_entities_feed_card_id"), "feed_card_entities", ["feed_card_id"], unique=False)
    op.create_index(op.f("ix_feed_card_entities_id"), "feed_card_entities", ["id"], unique=False)

    op.create_table(
        "feed_schedules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("feed_card_id", sa.Integer(), nullable=False),
        sa.Column("publish_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expire_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["feed_card_id"], ["feed_cards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feed_schedules_feed_card_id"), "feed_schedules", ["feed_card_id"], unique=False)
    op.create_index(op.f("ix_feed_schedules_id"), "feed_schedules", ["id"], unique=False)

    op.create_table(
        "trending_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("score_type", sa.String(length=60), server_default="manual_seed", nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trending_scores_entity_id"), "trending_scores", ["entity_id"], unique=False)
    op.create_index(op.f("ix_trending_scores_id"), "trending_scores", ["id"], unique=False)
    op.create_index(op.f("ix_trending_scores_score_type"), "trending_scores", ["score_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trending_scores_score_type"), table_name="trending_scores")
    op.drop_index(op.f("ix_trending_scores_id"), table_name="trending_scores")
    op.drop_index(op.f("ix_trending_scores_entity_id"), table_name="trending_scores")
    op.drop_table("trending_scores")

    op.drop_index(op.f("ix_feed_schedules_id"), table_name="feed_schedules")
    op.drop_index(op.f("ix_feed_schedules_feed_card_id"), table_name="feed_schedules")
    op.drop_table("feed_schedules")

    op.drop_index(op.f("ix_feed_card_entities_id"), table_name="feed_card_entities")
    op.drop_index(op.f("ix_feed_card_entities_feed_card_id"), table_name="feed_card_entities")
    op.drop_index(op.f("ix_feed_card_entities_entity_id"), table_name="feed_card_entities")
    op.drop_table("feed_card_entities")

    op.drop_index(op.f("ix_feed_cards_status"), table_name="feed_cards")
    op.drop_index(op.f("ix_feed_cards_region"), table_name="feed_cards")
    op.drop_index(op.f("ix_feed_cards_id"), table_name="feed_cards")
    op.drop_index(op.f("ix_feed_cards_created_by_user_id"), table_name="feed_cards")
    op.drop_index(op.f("ix_feed_cards_card_type"), table_name="feed_cards")
    op.drop_index(op.f("ix_feed_cards_approved_by_user_id"), table_name="feed_cards")
    op.drop_table("feed_cards")

    op.drop_index(op.f("ix_feed_regions_id"), table_name="feed_regions")
    op.drop_index(op.f("ix_feed_regions_code"), table_name="feed_regions")
    op.drop_table("feed_regions")
