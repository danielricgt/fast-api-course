from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.tag import TagORM
# this help us to do the db querys


class TagRepository():
    #  the constructor help to create the session on BD
    def __init__(self, db: Session):
        self.db = db

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
