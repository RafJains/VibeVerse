from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Community(Base):
    __tablename__ = "communities"
    __table_args__ = (
        CheckConstraint(
            "community_type IN ('fan', 'official', 'platform')",
            name="ck_communities_community_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'hidden')",
            name="ck_communities_status",
        ),
        UniqueConstraint("slug", name="uq_communities_slug"),
        UniqueConstraint("name", name="uq_communities_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    community_type: Mapped[str] = mapped_column(String(20), default="fan", nullable=False)
    entity_id: Mapped[int | None] = mapped_column(
        ForeignKey("entities.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    owner_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), default="approved", nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    banner_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    member_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="owned_communities")
    entity: Mapped["Entity | None"] = relationship(back_populates="communities")
    members: Mapped[list["CommunityMember"]] = relationship(
        back_populates="community",
        cascade="all, delete-orphan",
    )
    rules: Mapped[list["CommunityRule"]] = relationship(
        back_populates="community",
        cascade="all, delete-orphan",
        order_by="CommunityRule.order_index",
    )
    reports: Mapped[list["CommunityReport"]] = relationship(
        back_populates="community",
        cascade="all, delete-orphan",
    )
    source_merge_requests: Mapped[list["CommunityMergeRequest"]] = relationship(
        back_populates="source_community",
        cascade="all, delete-orphan",
        foreign_keys="CommunityMergeRequest.source_community_id",
    )
    target_merge_requests: Mapped[list["CommunityMergeRequest"]] = relationship(
        back_populates="target_community",
        cascade="all, delete-orphan",
        foreign_keys="CommunityMergeRequest.target_community_id",
    )


class CommunityMember(Base):
    __tablename__ = "community_members"
    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'moderator', 'member')",
            name="ck_community_members_role",
        ),
        CheckConstraint(
            "status IN ('active', 'banned', 'left')",
            name="ck_community_members_status",
        ),
        UniqueConstraint("community_id", "user_id", name="uq_community_members_community_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    community: Mapped[Community] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="community_memberships")


class CommunityRule(Base):
    __tablename__ = "community_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    community: Mapped[Community] = relationship(back_populates="rules")


class CommunityReport(Base):
    __tablename__ = "community_reports"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="ck_community_reports_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reporter_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(120), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    community: Mapped[Community] = relationship(back_populates="reports")
    reporter: Mapped["User"] = relationship(back_populates="community_reports")


class CommunityMergeRequest(Base):
    __tablename__ = "community_merge_requests"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="ck_community_merge_requests_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_community_id: Mapped[int] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    target_community_id: Mapped[int] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    requested_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    source_community: Mapped[Community] = relationship(
        back_populates="source_merge_requests",
        foreign_keys=[source_community_id],
    )
    target_community: Mapped[Community] = relationship(
        back_populates="target_merge_requests",
        foreign_keys=[target_community_id],
    )
    requested_by: Mapped["User"] = relationship(back_populates="community_merge_requests")
