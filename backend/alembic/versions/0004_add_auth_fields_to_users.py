"""add auth fields to users

Revision ID: 0004_add_auth_fields_to_users
Revises: 0003_create_collection_tables
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0004_add_auth_fields_to_users"
down_revision: Union[str, None] = "0003_create_collection_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TEMPORARY_HASHED_PASSWORD = "$2b$12$4sKeOLFhSLpRNbKD.cGybO0adn1/fcTGOcGa49a18A20plEic3/0G"


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255)")
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
        "updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()"
    )
    op.execute(
        f"UPDATE users SET hashed_password = '{TEMPORARY_HASHED_PASSWORD}' "
        "WHERE hashed_password IS NULL"
    )
    op.execute("UPDATE users SET updated_at = now() WHERE updated_at IS NULL")
    op.execute("ALTER TABLE users ALTER COLUMN hashed_password SET NOT NULL")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at SET DEFAULT now()")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at SET NOT NULL")

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_users_email'
            ) THEN
                ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_users_username'
            ) THEN
                ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username);
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_users_role'
            ) THEN
                ALTER TABLE users ADD CONSTRAINT ck_users_role
                CHECK (
                    role IN (
                        'guest',
                        'normal_user',
                        'community_owner',
                        'moderator',
                        'verified_user',
                        'admin',
                        'super_admin'
                    )
                );
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_role")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_users_username")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_users_email")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS updated_at")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS hashed_password")
