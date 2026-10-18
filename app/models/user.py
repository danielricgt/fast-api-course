

from datetime import datetime
from typing import List, Literal
from xmlrpc.client import boolean

from sqlalchemy import Boolean, DateTime, Enum, String

from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.post import PostORM

Role = Literal ["user", "admin", "editor"]

class User (Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hash_password : Mapped[str] = mapped_column(String(255), nullable=False)
    full_name : Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum("user","editor", "admin", name="role_enum"), default="user")
    is_active: Mapped[boolean] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
        # relation betwen author and postorm
    posts: Mapped[List["PostORM"]] = relationship(back_populates="user")
    
