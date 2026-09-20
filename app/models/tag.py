
from __future__ import annotations

from typing import List
from sqlalchemy.orm import joinedload, relationship, selectinload, sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, ForeignKey, Table, create_engine,   Integer, String, Text, DateTime, select, func, UniqueConstraint
from app.core.db import Base


from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .post import PostORM

class TagORM(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(190), unique=True)
    # n : n relationship we need a table to link the ids
    posts: Mapped[list["PostORM"]] = relationship(secondary= "post_tags",
                                                 back_populates="tags", 
                                                 lazy="selectin")
