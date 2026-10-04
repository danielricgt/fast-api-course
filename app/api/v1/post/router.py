from app.api.v1.post.schemas import (PostPublic, PaginatedPost,PostPublic, PostSummary, PostCreate, PostUpdate)
from app.core.db import get_db
from app.core.security import auth2_scheme, get_current_user
from app.core.security import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from math import ceil
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List, Literal, Optional, Union
import asyncio
import time
import threading


from app.api.v1.post.repository import PostRepository

router = APIRouter(prefix="/post", tags=["post"])

# @router.get("/sync")
# def sync_func():
#     print('SYNC thread', threading.current_thread().name)
#     time.sleep(8)
#     return {"message":"sync func finished"}

# @router.get('/async')
# async def async_funct():
#    print('ASYNC thread', threading.current_thread().name)
#    await  asyncio.sleep(8)
#    return {"message":"async func finished"}

def get_gake_user():
    return {"username":"daniel", "role":"admin"}


@router.get("/me")
def read_me(user: dict = Depends(get_gake_user)):
    return {"user": user}

@router.get("/secure") 
def secure_endpoint(token:str = Depends(auth2_scheme)):
    return {"message": "access with token", "token received":token}
 
@router.get("",response_model=PaginatedPost)
def list_post(
     query: Optional[str] = Query(
        default=None,
        description="search text",
    ),
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="obsolete paramter use query or serach instead",
),
    per_page: int = Query(
        10, ge=1, le=50, description="number result (1-10)",
),
    page: int = Query(
        1,
        ge=1,
        description="page number >= 1"
),
    order_by: Literal["id", "title"] = Query(
        "id", description="order field"
),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="order direction"
),
    db: Session = Depends(get_db)

):
    
    repository = PostRepository(db)
    query = query or text
    total, items = repository.search(query, order_by, direction, page, per_page)
    total_pages = ceil(total/per_page) if total > 0 else 0
    current_page = min(page, total_pages)

    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False
    
    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items)


@router.get("/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="one or more tags example ?tags=python&tags=fastapi"
    ),
    db : Session = Depends(get_db)
):
    
    repository = PostRepository(db)
    
    
    return repository.by_task(tags)
    
@router.get("/{post_id}", response_model=Union[PostPublic, PostSummary], response_description="Post found")
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title="post id",
    description="identifies has to be grater that one",
    example=1  
), include_content: bool = Query(default=True, description="discard content flag"),
        db: Session = Depends(get_db)):
    # look for id value indisde model in db
    repository = PostRepository(db)


    post =  repository.get(post_id)
    
    if not post:
            raise HTTPException(status_code=404, detail="post not found")
        # for post in BLOCK_POST:
        #     if post["id"] == post_id:
        #         if not include_content:
        #             return {"id": post["id"], "title": post["title"]}
        #         return post
    if include_content:
            return PostPublic.model_validate(post, from_attributes=True)
    
    return PostSummary.model_validate(post, from_attributes=True)
    

@router.post("", response_model=PostPublic, response_description="posts created", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):

    repository = PostRepository(db)
    
    try:
        post = repository.create_post(
            title=post.title, 
            content=post.content, 
            author=user,
            tags=[tag.model_dump()for tag in post.tags]
            )
        # confirm with a commit
        db.commit()
        #  bring the final values like id or created at
        db.refresh(post)
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="the title already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error creating the post")

@router.put("/{post_id}", response_model=PostPublic, response_description="post updated", response_model_exclude=None,)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    repository =PostRepository(db)
    
    post = repository.get(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    
    try:
        updates = data.model_dump(exclude_unset=True)
        post = repository.update_post(post, updates)
        db.commit()
                    #  bring the final values like id or created at
        db.refresh(post)
        return post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="an error has ocurred ")
    

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    repository = PostRepository(db)
    post = repository.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="postid not found")
    try:
        repository.delete_post(post)
        db.commit()
            
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="an error has ocurred")
    
