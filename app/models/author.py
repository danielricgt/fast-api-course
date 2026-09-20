from __future__ import annotations

from typing import List, TYPE_CHECKING
from sqlalchemy.orm import joinedload, relationship, selectinload, sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, ForeignKey, Table, create_engine,   Integer, String, Text, DateTime, select, func, UniqueConstraint
from app.core.db import Base

from app.models.post import PostORM

if TYPE_CHECKING:
    from .post import PostORM

class AuthorORM(Base):
    __tablename__ = 'author'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    # relation betwen author and postorm
    posts: Mapped[List["PostORM"]] = relationship(back_populates="author")
