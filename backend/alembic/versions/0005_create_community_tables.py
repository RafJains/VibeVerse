"""create community tables

Revision ID: 0005_create_community_tables
Revises: 0004_add_auth_fields_to_users
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_create_community_tables"
down_revision: Union[str, None] = "0004_add_auth_fields_to_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "communities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("community_type", sa.String(length=20), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("banner_url", sa.String(length=1000), nullable=True),
        sa.Column("member_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "community_type IN ('fan', 'official', 'platform')",
            name="ck_communities_community_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'hidden')",
            name="ck_communities_status",
        ),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_communities_name"),
        sa.UniqueConstraint("slug", name="uq_communities_slug"),
    )
    op.create_index(op.f("ix_communities_community_type"), "communities", ["community_type"], unique=False)
    op.create_index(op.f("ix_communities_entity_id"), "communities", ["entity_id"], unique=False)
    op.create_index(op.f("ix_communities_id"), "communities", ["id"], unique=False)
    op.create_index(op.f("ix_communities_owner_user_id"), "communities", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_communities_status"), "communities", ["status"], unique=False)

    op.create_table(
        "community_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("community_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "role IN ('owner', 'moderator', 'member')",
            name="ck_community_members_role",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'banned', 'left')",
            name="ck_community_members_status",
        ),
        sa.ForeignKeyConstraint(["community_id"], ["communities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("community_id", "user_id", name="uq_community_members_community_user"),
    )
    op.create_index(op.f("ix_community_members_community_id"), "community_members", ["community_id"], unique=False)
    op.create_index(op.f("ix_community_members_id"), "community_members", ["id"], unique=False)
    op.create_index(op.f("ix_community_members_user_id"), "community_members", ["user_id"], unique=False)

    op.create_table(
        "community_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("community_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["community_id"], ["communities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_community_rules_community_id"), "community_rules", ["community_id"], unique=False)
    op.create_index(op.f("ix_community_rules_id"), "community_rules", ["id"], unique=False)

    op.create_table(
        "community_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("community_id", sa.Integer(), nullable=False),
        sa.Column("reporter_user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="ck_community_reports_status",
        ),
        sa.ForeignKeyConstraint(["community_id"], ["communities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reporter_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_community_reports_community_id"), "community_reports", ["community_id"], unique=False)
    op.create_index(op.f("ix_community_reports_id"), "community_reports", ["id"], unique=False)
    op.create_index(op.f("ix_community_reports_reporter_user_id"), "community_reports", ["reporter_user_id"], unique=False)

    op.create_table(
        "community_merge_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_community_id", sa.Integer(), nullable=False),
        sa.Column("target_community_id", sa.Integer(), nullable=False),
        sa.Column("requested_by_user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="ck_community_merge_requests_status",
        ),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_community_id"], ["communities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_community_id"], ["communities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_community_merge_requests_id"),
        "community_merge_requests",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_community_merge_requests_requested_by_user_id"),
        "community_merge_requests",
        ["requested_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_community_merge_requests_source_community_id"),
        "community_merge_requests",
        ["source_community_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_community_merge_requests_target_community_id"),
        "community_merge_requests",
        ["target_community_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_community_merge_requests_target_community_id"), table_name="community_merge_requests")
    op.drop_index(op.f("ix_community_merge_requests_source_community_id"), table_name="community_merge_requests")
    op.drop_index(op.f("ix_community_merge_requests_requested_by_user_id"), table_name="community_merge_requests")
    op.drop_index(op.f("ix_community_merge_requests_id"), table_name="community_merge_requests")
    op.drop_table("community_merge_requests")

    op.drop_index(op.f("ix_community_reports_reporter_user_id"), table_name="community_reports")
    op.drop_index(op.f("ix_community_reports_id"), table_name="community_reports")
    op.drop_index(op.f("ix_community_reports_community_id"), table_name="community_reports")
    op.drop_table("community_reports")

    op.drop_index(op.f("ix_community_rules_id"), table_name="community_rules")
    op.drop_index(op.f("ix_community_rules_community_id"), table_name="community_rules")
    op.drop_table("community_rules")

    op.drop_index(op.f("ix_community_members_user_id"), table_name="community_members")
    op.drop_index(op.f("ix_community_members_id"), table_name="community_members")
    op.drop_index(op.f("ix_community_members_community_id"), table_name="community_members")
    op.drop_table("community_members")

    op.drop_index(op.f("ix_communities_status"), table_name="communities")
    op.drop_index(op.f("ix_communities_owner_user_id"), table_name="communities")
    op.drop_index(op.f("ix_communities_id"), table_name="communities")
    op.drop_index(op.f("ix_communities_entity_id"), table_name="communities")
    op.drop_index(op.f("ix_communities_community_type"), table_name="communities")
    op.drop_table("communities")
