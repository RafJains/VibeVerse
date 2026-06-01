"""create core entity tables

Revision ID: 0001_create_core_entity_tables
Revises:
Create Date: 2026-06-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_create_core_entity_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


entity_type_enum = postgresql.ENUM(
    "film",
    "series",
    "song",
    "album",
    "game",
    "sport",
    "tournament",
    "team",
    "person",
    "live_event",
    name="entity_type_enum",
    create_type=False,
)


def upgrade() -> None:
    entity_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "entities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("entity_type", entity_type_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("release_date", sa.Date(), nullable=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("banner_url", sa.String(length=1000), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("popularity_score", sa.Float(), nullable=False),
        sa.Column("canonical_entity_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["canonical_entity_id"], ["entities.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entities_entity_type"), "entities", ["entity_type"], unique=False)
    op.create_index(op.f("ix_entities_id"), "entities", ["id"], unique=False)
    op.create_index(op.f("ix_entities_name"), "entities", ["name"], unique=False)

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_profiles_id"), "profiles", ["id"], unique=False)
    op.create_index(op.f("ix_profiles_user_id"), "profiles", ["user_id"], unique=True)

    op.create_table(
        "entity_aliases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entity_aliases_alias"), "entity_aliases", ["alias"], unique=False)
    op.create_index(op.f("ix_entity_aliases_entity_id"), "entity_aliases", ["entity_id"], unique=False)
    op.create_index(op.f("ix_entity_aliases_id"), "entity_aliases", ["id"], unique=False)

    op.create_table(
        "entity_media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("media_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=1000), nullable=True),
        sa.Column("source_name", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entity_media_entity_id"), "entity_media", ["entity_id"], unique=False)
    op.create_index(op.f("ix_entity_media_id"), "entity_media", ["id"], unique=False)

    op.create_table(
        "entity_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("tag", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entity_tags_entity_id"), "entity_tags", ["entity_id"], unique=False)
    op.create_index(op.f("ix_entity_tags_id"), "entity_tags", ["id"], unique=False)
    op.create_index(op.f("ix_entity_tags_tag"), "entity_tags", ["tag"], unique=False)

    op.create_table(
        "entity_credits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("person_entity_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False),
        sa.Column("character_name", sa.String(length=255), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["person_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entity_credits_entity_id"), "entity_credits", ["entity_id"], unique=False)
    op.create_index(op.f("ix_entity_credits_id"), "entity_credits", ["id"], unique=False)
    op.create_index(op.f("ix_entity_credits_person_entity_id"), "entity_credits", ["person_entity_id"], unique=False)

    op.create_table(
        "entity_relations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_entity_id", sa.Integer(), nullable=False),
        sa.Column("target_entity_id", sa.Integer(), nullable=False),
        sa.Column("relation_type", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entity_relations_id"), "entity_relations", ["id"], unique=False)
    op.create_index(op.f("ix_entity_relations_source_entity_id"), "entity_relations", ["source_entity_id"], unique=False)
    op.create_index(op.f("ix_entity_relations_target_entity_id"), "entity_relations", ["target_entity_id"], unique=False)

    op.create_table(
        "external_ids",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("source_name", sa.String(length=100), nullable=False),
        sa.Column("source_entity_id", sa.String(length=255), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_external_ids_entity_id"), "external_ids", ["entity_id"], unique=False)
    op.create_index(op.f("ix_external_ids_id"), "external_ids", ["id"], unique=False)
    op.create_index(op.f("ix_external_ids_source_entity_id"), "external_ids", ["source_entity_id"], unique=False)
    op.create_index(op.f("ix_external_ids_source_name"), "external_ids", ["source_name"], unique=False)

    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_name", sa.String(length=100), nullable=False),
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingestion_jobs_id"), "ingestion_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_ingestion_jobs_source_name"), "ingestion_jobs", ["source_name"], unique=False)
    op.create_index(op.f("ix_ingestion_jobs_status"), "ingestion_jobs", ["status"], unique=False)

    op.create_table(
        "raw_external_payloads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_name", sa.String(length=100), nullable=False),
        sa.Column("source_entity_id", sa.String(length=255), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_raw_external_payloads_id"), "raw_external_payloads", ["id"], unique=False)
    op.create_index(op.f("ix_raw_external_payloads_source_entity_id"), "raw_external_payloads", ["source_entity_id"], unique=False)
    op.create_index(op.f("ix_raw_external_payloads_source_name"), "raw_external_payloads", ["source_name"], unique=False)

    op.create_table(
        "user_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_events_entity_id"), "user_events", ["entity_id"], unique=False)
    op.create_index(op.f("ix_user_events_event_type"), "user_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_user_events_id"), "user_events", ["id"], unique=False)
    op.create_index(op.f("ix_user_events_user_id"), "user_events", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_events_user_id"), table_name="user_events")
    op.drop_index(op.f("ix_user_events_id"), table_name="user_events")
    op.drop_index(op.f("ix_user_events_event_type"), table_name="user_events")
    op.drop_index(op.f("ix_user_events_entity_id"), table_name="user_events")
    op.drop_table("user_events")

    op.drop_index(op.f("ix_raw_external_payloads_source_name"), table_name="raw_external_payloads")
    op.drop_index(op.f("ix_raw_external_payloads_source_entity_id"), table_name="raw_external_payloads")
    op.drop_index(op.f("ix_raw_external_payloads_id"), table_name="raw_external_payloads")
    op.drop_table("raw_external_payloads")

    op.drop_index(op.f("ix_ingestion_jobs_status"), table_name="ingestion_jobs")
    op.drop_index(op.f("ix_ingestion_jobs_source_name"), table_name="ingestion_jobs")
    op.drop_index(op.f("ix_ingestion_jobs_id"), table_name="ingestion_jobs")
    op.drop_table("ingestion_jobs")

    op.drop_index(op.f("ix_external_ids_source_name"), table_name="external_ids")
    op.drop_index(op.f("ix_external_ids_source_entity_id"), table_name="external_ids")
    op.drop_index(op.f("ix_external_ids_id"), table_name="external_ids")
    op.drop_index(op.f("ix_external_ids_entity_id"), table_name="external_ids")
    op.drop_table("external_ids")

    op.drop_index(op.f("ix_entity_relations_target_entity_id"), table_name="entity_relations")
    op.drop_index(op.f("ix_entity_relations_source_entity_id"), table_name="entity_relations")
    op.drop_index(op.f("ix_entity_relations_id"), table_name="entity_relations")
    op.drop_table("entity_relations")

    op.drop_index(op.f("ix_entity_credits_person_entity_id"), table_name="entity_credits")
    op.drop_index(op.f("ix_entity_credits_id"), table_name="entity_credits")
    op.drop_index(op.f("ix_entity_credits_entity_id"), table_name="entity_credits")
    op.drop_table("entity_credits")

    op.drop_index(op.f("ix_entity_tags_tag"), table_name="entity_tags")
    op.drop_index(op.f("ix_entity_tags_id"), table_name="entity_tags")
    op.drop_index(op.f("ix_entity_tags_entity_id"), table_name="entity_tags")
    op.drop_table("entity_tags")

    op.drop_index(op.f("ix_entity_media_id"), table_name="entity_media")
    op.drop_index(op.f("ix_entity_media_entity_id"), table_name="entity_media")
    op.drop_table("entity_media")

    op.drop_index(op.f("ix_entity_aliases_id"), table_name="entity_aliases")
    op.drop_index(op.f("ix_entity_aliases_entity_id"), table_name="entity_aliases")
    op.drop_index(op.f("ix_entity_aliases_alias"), table_name="entity_aliases")
    op.drop_table("entity_aliases")

    op.drop_index(op.f("ix_profiles_user_id"), table_name="profiles")
    op.drop_index(op.f("ix_profiles_id"), table_name="profiles")
    op.drop_table("profiles")

    op.drop_index(op.f("ix_entities_name"), table_name="entities")
    op.drop_index(op.f("ix_entities_id"), table_name="entities")
    op.drop_index(op.f("ix_entities_entity_type"), table_name="entities")
    op.drop_table("entities")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    entity_type_enum.drop(op.get_bind(), checkfirst=True)
