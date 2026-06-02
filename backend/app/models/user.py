from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('guest', 'normal_user', 'community_owner', 'moderator', 'verified_user', 'admin', 'super_admin')",
            name="ck_users_role",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="normal_user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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

    profile: Mapped["Profile | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["UserEvent"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    review_reports: Mapped[list["ReviewReport"]] = relationship(back_populates="reporter")
    collections: Mapped[list["Collection"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    owned_communities: Mapped[list["Community"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    community_memberships: Mapped[list["CommunityMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    community_reports: Mapped[list["CommunityReport"]] = relationship(back_populates="reporter")
    community_merge_requests: Mapped[list["CommunityMergeRequest"]] = relationship(
        back_populates="requested_by",
    )
    community_posts: Mapped[list["CommunityPost"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    post_reports: Mapped[list["PostReport"]] = relationship(back_populates="reporter")
    post_moderation_actions: Mapped[list["PostModerationAction"]] = relationship(
        back_populates="moderator",
    )
    community_blocked_words: Mapped[list["CommunityBlockedWord"]] = relationship(
        back_populates="created_by",
    )
    created_feed_cards: Mapped[list["FeedCard"]] = relationship(
        back_populates="creator",
        foreign_keys="FeedCard.created_by_user_id",
    )
    approved_feed_cards: Mapped[list["FeedCard"]] = relationship(
        back_populates="approver",
        foreign_keys="FeedCard.approved_by_user_id",
    )


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
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

    user: Mapped[User] = relationship(back_populates="profile")
