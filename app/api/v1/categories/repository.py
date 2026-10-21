
from typing import Sequence, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import CategoryORM


class CategoryRepository:
    
    def __init__(self, db: Session):
        self.db = db
    def list_many(self, *, skip: int = 0, limit: int = 50) -> Sequence[CategoryORM]:
        query = (select (CategoryORM).offset(skip).limit(limit))
        return self.db.execute(query).scalars().all()
    
    def list_with_total(self, * , page: int = 1, per_page: int = 50) -> Tuple[int, list[CategoryORM]]:
        total = (select(CategoryORM).offset)
        
    def get(self, category_id: int) -> CategoryORM | None:
        return self.db.get(CategoryORM,category_id )
    
    def get_by_slug(self, slug: str) -> CategoryORM | None:
        query = select(CategoryORM).where(CategoryORM.slug == slug )
        return self.db.execute(query).scalars().first() 
    
    def create(self, * , name: str, slug : str) -> CategoryORM:
        category = CategoryORM(name= name, slug = slug)
        self.db.add(category)
        self.db.flush()
        return category
    
    def update(self, category: CategoryORM, updates: dict) -> CategoryORM:
        # allow_items = {"name" , "slug"}
        for key, value in updates.items():
            setattr (category, key, value)
        self.db.add(category)
        self.db.flush()
        return category
            
             
    def delete (self, category: CategoryORM) -> None:
        
        self.db.delete(category)