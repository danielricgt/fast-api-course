from sqlalchemy import Integer, String

from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CategoryORM(Base):
    __tablename__ = "categories"
    id = Mapped[int]  = mapped_column(Integer(245), index= True, primary_key=True)
    name = Mapped[str] = mapped_column(String(32), unique=True, index=True)
    slug = Mapped[str] = mapped_column(String(32), unique=True, index=True)
    
    # backpopulate indicate how im gonna communicate in the other why how post access to category
    post = relationship(
        "PostORM", back_populates="category", cascade="all, delete", passive_deletes=True)
    
    
    