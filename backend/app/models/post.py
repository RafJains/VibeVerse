from datetime import datetime

from sqlalchemy import (
    Boolean,
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


class CommunityPost(Base):
    __tablename__ = "community_posts"
    __table_args__ = (
        CheckConstraint(
            "post_type IN ('review', 'hot_take', 'poll', 'meme_edit', 'fan_theory', "
            "'reaction', 'ranking', 'cover_clip', 'discussion')",
            name="ck_community_posts_post_type",
        ),
        CheckConstraint(
            "status IN ('published', 'hidden', 'removed')",
            name="ck_community_posts_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    author_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    post_type: Mapped[str] = mapped_column(String(30), default="discussion", nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    spoiler: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="published", nullable=False)
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

    community: Mapped["Community"] = relationship(back_populates="posts")
    author: Mapped["User"] = relationship(back_populates="community_posts")
    reports: Mapped[list["PostReport"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )
    moderation_actions: Mapped[list["PostModerationAction"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )


class PostReport(Base):
    __tablename__ = "post_reports"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="ck_post_reports_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("community_posts.id", ondelete="CASCADE"),
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

    post: Mapped[CommunityPost] = relationship(back_populates="reports")
    reporter: Mapped["User"] = relationship(back_populates="post_reports")


class PostModerationAction(Base):
    __tablename__ = "post_moderation_actions"
    __table_args__ = (
        CheckConstraint(
            "action_type IN ('hide', 'unhide', 'remove', 'restore')",
            name="ck_post_moderation_actions_action_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("community_posts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    moderator_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    action_type: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    post: Mapped[CommunityPost] = relationship(back_populates="moderation_actions")
    moderator: Mapped["User"] = relationship(back_populates="post_moderation_actions")


class CommunityBlockedWord(Base):
    __tablename__ = "community_blocked_words"
    __table_args__ = (
        UniqueConstraint("community_id", "word", name="uq_community_blocked_words_word"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    word: Mapped[str] = mapped_column(String(120), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    community: Mapped["Community"] = relationship(back_populates="blocked_words")
    created_by: Mapped["User"] = relationship(back_populates="community_blocked_words")
