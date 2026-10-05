from __future__ import annotations
from typing import List, TYPE_CHECKING
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, ForeignKey, Table, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.db import Base

if TYPE_CHECKING:
    from .author import AuthorORM
    from .tag import TagORM

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)


class PostORM(Base):
    # table_name
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)
    # data attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    image_url = mapped_column(String(200), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)
    # relationship with author table(foreign key)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("author.id"), nullable=True)
    author: Mapped[Optional["AuthorORM"]] = relationship(
        back_populates="posts")
    tags: Mapped[List["TagORM"]] = relationship(secondary="post_tags",
                                                back_populates="posts",
                                                lazy="selectin",
                                                passive_deletes=True)

