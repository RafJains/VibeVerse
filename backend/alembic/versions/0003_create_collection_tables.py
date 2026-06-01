"""create collection tables

Revision ID: 0003_create_collection_tables
Revises: 0002_create_review_tables
Create Date: 2026-06-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_create_collection_tables"
down_revision: Union[str, None] = "0002_create_review_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("collection_type", sa.String(length=40), nullable=False),
        sa.Column("visibility", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "collection_type IN ('watchlist', 'playlist', 'favourites', 'custom_collection', 'gamelist')",
            name="ck_collections_collection_type",
        ),
        sa.CheckConstraint(
            "visibility IN ('public', 'private', 'followers')",
            name="ck_collections_visibility",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_collections_collection_type"), "collections", ["collection_type"], unique=False)
    op.create_index(op.f("ix_collections_id"), "collections", ["id"], unique=False)
    op.create_index(op.f("ix_collections_user_id"), "collections", ["user_id"], unique=False)

    op.create_table(
        "collection_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_id", "entity_id", name="uq_collection_items_collection_entity"),
    )
    op.create_index(op.f("ix_collection_items_collection_id"), "collection_items", ["collection_id"], unique=False)
    op.create_index(op.f("ix_collection_items_entity_id"), "collection_items", ["entity_id"], unique=False)
    op.create_index(op.f("ix_collection_items_id"), "collection_items", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_collection_items_id"), table_name="collection_items")
    op.drop_index(op.f("ix_collection_items_entity_id"), table_name="collection_items")
    op.drop_index(op.f("ix_collection_items_collection_id"), table_name="collection_items")
    op.drop_table("collection_items")

    op.drop_index(op.f("ix_collections_user_id"), table_name="collections")
    op.drop_index(op.f("ix_collections_id"), table_name="collections")
    op.drop_index(op.f("ix_collections_collection_type"), table_name="collections")
    op.drop_table("collections")
