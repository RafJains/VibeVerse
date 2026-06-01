from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "entity_id", name="uq_reviews_user_entity"),
        CheckConstraint("rating >= 0.5 AND rating <= 5.0", name="ck_reviews_rating_range"),
        CheckConstraint(
            "visibility IN ('public', 'followers', 'private')",
            name="ck_reviews_visibility",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    spoiler: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), default="public", nullable=False)
    attachment_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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

    entity: Mapped["Entity"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")
    tags: Mapped[list["ReviewTag"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )
    edit_history: Mapped[list["ReviewEditHistory"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )
    reports: Mapped[list["ReviewReport"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )


class ReviewTag(Base):
    __tablename__ = "review_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    review: Mapped[Review] = relationship(back_populates="tags")


class ReviewEditHistory(Base):
    __tablename__ = "review_edit_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    previous_rating: Mapped[float] = mapped_column(Float, nullable=False)
    previous_title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    previous_body: Mapped[str] = mapped_column(Text, nullable=False)
    previous_spoiler: Mapped[bool] = mapped_column(Boolean, nullable=False)
    previous_visibility: Mapped[str] = mapped_column(String(20), nullable=False)
    previous_attachment_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    edited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    review: Mapped[Review] = relationship(back_populates="edit_history")


class ReviewReport(Base):
    __tablename__ = "review_reports"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="ck_review_reports_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
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

    review: Mapped[Review] = relationship(back_populates="reports")
    reporter: Mapped["User"] = relationship(back_populates="review_reports")
