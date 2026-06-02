from datetime import datetime

from sqlalchemy import (
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


class FeedCard(Base):
    __tablename__ = "feed_cards"
    __table_args__ = (
        CheckConstraint(
            "card_type IN ('trending_entity', 'new_release', 'trailer_drop', 'top_chart', "
            "'spotlight', 'official_update', 'recommendation', 'announcement')",
            name="ck_feed_cards_card_type",
        ),
        CheckConstraint(
            "status IN ('draft', 'pending_review', 'approved', 'rejected', 'published', 'archived')",
            name="ck_feed_cards_status",
        ),
        CheckConstraint(
            "source_type IN ('admin_created', 'system_suggested', 'external_ingestion')",
            name="ck_feed_cards_source_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    card_type: Mapped[str] = mapped_column(String(40), default="spotlight", index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_type: Mapped[str] = mapped_column(String(40), default="admin_created", nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    region: Mapped[str | None] = mapped_column(
        ForeignKey("feed_regions.code", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    approved_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    creator: Mapped["User"] = relationship(
        back_populates="created_feed_cards",
        foreign_keys=[created_by_user_id],
    )
    approver: Mapped["User | None"] = relationship(
        back_populates="approved_feed_cards",
        foreign_keys=[approved_by_user_id],
    )
    entities: Mapped[list["FeedCardEntity"]] = relationship(
        back_populates="feed_card",
        cascade="all, delete-orphan",
        order_by="FeedCardEntity.order_index",
    )
    schedules: Mapped[list["FeedSchedule"]] = relationship(
        back_populates="feed_card",
        cascade="all, delete-orphan",
    )
    feed_region: Mapped["FeedRegion | None"] = relationship(back_populates="feed_cards")


class FeedCardEntity(Base):
    __tablename__ = "feed_card_entities"
    __table_args__ = (
        UniqueConstraint("feed_card_id", "entity_id", name="uq_feed_card_entities_card_entity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feed_card_id: Mapped[int] = mapped_column(
        ForeignKey("feed_cards.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    feed_card: Mapped[FeedCard] = relationship(back_populates="entities")
    entity: Mapped["Entity"] = relationship(back_populates="feed_card_links")


class FeedSchedule(Base):
    __tablename__ = "feed_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feed_card_id: Mapped[int] = mapped_column(
        ForeignKey("feed_cards.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    publish_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expire_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    feed_card: Mapped[FeedCard] = relationship(back_populates="schedules")


class FeedRegion(Base):
    __tablename__ = "feed_regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    feed_cards: Mapped[list[FeedCard]] = relationship(back_populates="feed_region")


class TrendingScore(Base):
    __tablename__ = "trending_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    score_type: Mapped[str] = mapped_column(String(60), default="manual_seed", index=True, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    entity: Mapped["Entity"] = relationship(back_populates="trending_scores")
