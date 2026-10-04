from math import ceil
from typing import List, Optional, Tuple
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, relationship, selectinload, sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from app.models import PostORM, TagORM, AuthorORM


class PostRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:
        post_find = select(PostORM).where(PostORM.id == post_id)
        return self.db.execute(post_find).scalar_one_or_none()

    def search(self, 
               query: Optional[str],
               order_by: str,
               direction: str,
               page: str,
               per_page: str
               ) -> Tuple[int, list[PostORM]]:
        
        results = select(PostORM)
        if query:
            # list compression
            # result = []
            results = results.where(PostORM.title.ilike(f"%{query}%"))
            # for  post in BLOCK_POST:
            #     if query.lower() in post["title"].lower():
            #         result.append(post)
        total = self.db.scalar(select(func.count()).select_from(
            results.subquery()
        )) or 0
        
        if total == 0 :
            return 0, []



        current_page =  min((page, max(1, ceil(total/per_page))))
        # if total_pages == 0:
        #     current_page = 1
        # else:
        #     current_page = min(page, total_pages)
        order_col = PostORM.id if order_by == "id" else order_by == "id"

        results = results.order_by(
            order_col.asc() if direction == "asc" else order_col.desc())

    
        start = (current_page - 1) * per_page
        items = self.db.execute(results.limit(
            per_page).offset(start)).scalars().all()  # [10,20]
        return total, items
    
    def by_task(self, tags: List[str] ) -> List[PostORM]:

        normalize_tag_names = [tag.strip().lower()for tag in tags if tag.strip()]
        if not normalize_tag_names:
            return []
    
        post_list = (
            select(PostORM)
            .options(
                selectinload(PostORM.tags),
                joinedload(PostORM.author),
            ).where(PostORM.tags.any(func.lower(TagORM.name).in_(normalize_tag_names)))
        ).order_by(PostORM.id.asc())
        return self.db.execute(post_list).scalars().all()
        

    def ensure_author(self, name: str, email: str) -> AuthorORM:
       
        author_obj = self.db.execute(
            select(AuthorORM).where(AuthorORM.email ==email)
        ).scalar_one_or_none()

        if  author_obj:
            return author_obj
        
        author_obj = AuthorORM(name= name, email = email)                      

        self.db.add(author_obj)
                # secure it has an id
        self.db.flush()
        return author_obj
    
    
    
    def ensure_tag(self, name: str) -> TagORM:
        tag_obj = self.db.execute(
            select(TagORM).where(TagORM.name.ilike (name))
        ).scalar_one_or_none()

        if tag_obj:
            return tag_obj
        
        tag_obj = TagORM(name=name)
        self.db.add(tag_obj) 
        self.db.flush() 
        return tag_obj
    
    def create_post(self, title: str, content: str, author: Optional[dict], tags: List[dict]) -> PostORM :
        
        author_object = None
        if author:
            author_object = self.ensure_author(author['username'], author['email'])
        post = PostORM(title= title, content = content, author = author_object )
        
        for tag in tags:
            tag_obj = self.ensure_tag(tag['name']) 
            post.tags.append(tag_obj)
            
            self.db.add(post)
            self.db.flush()
            self.db.refresh(post)
        return post
    
    def update_post(self, post: PostORM, updates: dict) -> PostORM:
        # post = self.db.get(PostORM, post_id)
        # if not post:
        #         raise HTTPException(status_code=404, detail="post not found")

        # updates = update.model_dump(exclude_unset=True)
        for key, value in updates.items():
          setattr(post, key, value)

        return post
          
        
    def delete_post(self, post: PostORM) -> None:

        # post = self.db.get(PostORM, post_id)
        # if not post:
        #     raise HTTPException(status_code=404, detail="postid not found")

        self.db.delete(post)
