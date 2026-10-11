import code

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.post import repository
from app.api.v1.tags.schemas import TagCreate
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.tags.schemas import TagPublic
from app.api.v1.tags.repository import TagRepository
from app.core.db import get_db
from app.core.security import get_current_user


router = APIRouter(prefix="/tag",tags=["tags"])

@router.post("", response_model=TagPublic, response_description="Post Created", status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db), user= Depends(get_current_user)):  
    repository = TagRepository(db)
    try: 
        tag_created = repository.create_tag(name=tag.name)
        db.commit()
        db.refresh(tag_created)
        
    except  SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error creating the tag")
    return tag_created