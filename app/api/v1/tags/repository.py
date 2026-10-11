from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.tags.schemas import TagPublic
from app.models.tag import TagORM
from app.services.pagination import paginated_query
# this help us to do the db querys


class TagRepository():
    #  the constructor help to create the session on BD
    def __init__(self, db: Session):
        self.db = db

    def list_tags(self, 
        search: Optional[str],
        order_by: str = "id",
        direction: str = "asc",
        page: int  = 1,
        per_page: int = 10
        ):
    
        query = select(TagORM)
        if search : 
            query = query.where(func.lower(TagORM.name).ilike(f"%{search.lower()}%"))
        allowed_order = {
            "id": TagORM.id,
            "name": func.lower(TagORM.name)
        }
        result = paginated_query(
            db = self.db,
            model = TagORM,
            base_query= query,
            page= page,
            per_page= per_page,
            order_by= order_by,
            direction= direction,
            allowed_order= allowed_order
        )
        
        # this convert from models or orm objetx to an equivalent on pydanctic
        result["items"] = [TagPublic.model_validate(item) for item in result["items"]]]
         
        return result



    def create_tag(self, name: str):
       normalized = name.strip().lower()
       tag_obj = self.db.execute(
           select(TagORM).where(func.lower(TagORM.name) == normalized)
       ).scalar_one_or_none()

       if tag_obj:

           return tag_obj

       tag_obj = TagORM(name=name)
       self.db.add(tag_obj)
       self.db.flush()
       return tag_obj
