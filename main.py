import os
from datetime import datetime
from fastapi import FastAPI, Query, Body, HTTPException, Path, status, Depends
from pydantic import BaseModel, Field,  field_validator, EmailStr, ConfigDict
from typing import Optional, List, Union, Literal
from math import ceil
from sqlalchemy import Column, ForeignKey, Table, create_engine,   Integer, String, Text, DateTime, select, func, UniqueConstraint
from sqlalchemy.orm import joinedload, relationship, selectinload, sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from dotenv import load_dotenv

# we need to upload the .env
load_dotenv()
# recon .env file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
print("conected to", DATABASE_URL)
# configure at leat a local database
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
# creating the conection
engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)
# creating the session
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session)

# declarative base help us to define orm models as classes


class Base(DeclarativeBase):
    pass

# we create this callse to represent models un the database


post_tags = Table(
    "post-tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)
class TagORM(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(190), unique=True)
    # n : n relationship we need a table to link the ids
    posts: Mapped[list["PostORM"]] = relationship(secondary= post_tags,
                                                 back_populates="tags", 
                                                 lazy="selectin")




class AuthorORM(Base):
    __tablename__ = 'author'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    # relation betwen author and postorm
    posts: Mapped[List[PostORM]] = relationship(back_populates="author")


class PostORM(Base):
    # table_name
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)
    # data attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)
    # relationship with author table(foreign key)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("author.id"), nullable=True)
    author: Mapped[Optional["AuthorORM"]] = relationship(
        back_populates="posts")
    tags: Mapped[List["TagORM"]] = relationship(secondary=post_tags,
                                                back_populates="posts",
                                                lazy="selectin",
                                                passive_deletes=True)


# method that create if the db does not exists      #
Base.metadata.create_all(bind=engine)  # dev


def get_db():
    db = SessionLocal()
    try:
        # generativde expression
        yield db
    finally:
        # always close database connection
        db.close()


app = FastAPI(title='mini Bloc')

# BLOCK_POST = [{"id": 1, "title": "Hi from fastapi", "content": "the frist post with api"},
#               {"id": 2, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 3, "title": "second form fastapi", "content": "devtalles",
#                "tags": [
#                    {"name": "python"},
#                    {"name": "fastapi"}
#                ]},
#               {"id": 4, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 5, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 6, "title": "second form fastapi", "content": "devtalles", },
#               {"id": 7, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 8, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 9, "title": "second form fastapi", "content": "devtalles",  "tags": [
#                                  {"name": "python"},
#                                  {"name": "fastapi"}
#               ]},
#               {"id": 10, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 11, "title": "second form fastapi", "content": "devtalles",  "tags": [
#                   {"name": "python"},
#                   {"name": "fastapi"}
#               ]},
#               {"id": 12, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 13, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 14, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 15, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 16, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 17, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 18, "title": "second form fastapi", "content": "devtalles"},
#               {"id": 19, "title": "second form fastapi", "content": "devtalles",  "tags": [
#                   {"name": "python"},
#                   {"name": "fastapi"}
#               ]}]


class Tag (BaseModel):
    name: str = Field(
        ...,
        max_length=30,
        min_length=3,
        description="Tag name"
    )
    # here to receive objects not only dictionalt
    model_config =ConfigDict(from_attributes=True)


class Author (BaseModel):
    name: str
    email: EmailStr
    model_config =ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    # HERE we create the data strcuture and attrinutes you wanto to have
    title: str
    content: str 
    # create a list for every object created
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None
    model_config =ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Post title min 3 car max 100 car",
        examples=[
            "mi first post with fast api"
        ]
    )
    content: Optional[str] = Field(
        default="Pending content",
        min_length=10,
        description="bloc content",
        examples=[
            "This is a valid content cause has 10 or more caracters"
        ]
    )
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    author: Optional[Author] = None

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        not_allow_words = ['sex', 'porn', 'xxx', 'gay', 'dick', 'fuck']
        for word in not_allow_words:
            if word in value.lower():
                raise ValueError(f"title cannot contain {word} value ")
        return value


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=4, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str
    # i m=am going to validate this psot sumary from am object not only dictionaries
    model_config = ConfigDict(from_attributes=True)


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]  # its like a enum
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: list[PostPublic]  # i can add my ouwn types


@app.get("/")
def home():
    return {'message': 'welcome to my bloc from daniel galvan '}

# query parameter are for filtering
# ordering and pagination


@app.get("/posts/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="one or more tags example ?tags=python&tags=fastapi"
    ),
    db : Session = Depends(get_db)
):
    normalize_tag_names = [tag.strip().lower() for tag in tags if tag.strip()]
    if not normalize_tag_names: 
        return []
    
    post_list = (
        select(PostORM)
        .options(
            selectinload(PostORM.tags),
            joinedload(PostORM.author),
        ).where(PostORM.tags.any(func.lower(TagORM.name).in_(normalize_tag_names)))
    ).order_by(PostORM.id.asc())
    posts = db.execute(post_list).scalars().all()
    return posts


@app.get("/posts", response_model=PaginatedPost)
def bloc(query: Optional[str] = Query(
    default=None,
    description="Text to find by title",
    alias="search",
    min_length=3,
    max_length=32,
    pattern=r"^[\w\sáéíóúÁÉÍÓÚÜü-]+$"
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

    results = select(PostORM)
    query = query or text
    if query:
        # list compression
        # result = []
        results = results.where(PostORM.title.ilike(f"%{query}%"))
        # for  post in BLOCK_POST:
        #     if query.lower() in post["title"].lower():
        #         result.append(post)
    total = db.scalar(select(func.count()).select_from(
        results.subquery()
    )) or 0

    total_pages = ceil(total/per_page) if total > 0 else 0

    current_page = 1 if total_pages == 0 else min((page, total_pages))
    # if total_pages == 0:
    #     current_page = 1
    # else:
    #     current_page = min(page, total_pages)

    if order_by == "id":
        order_col = PostORM.id
    else:
        order_col = func.lower(PostORM.title)
    # results = sorted(
    #     results, key=lambda post: post[order_by],
    #     reverse=(direction == "desc"))

    results = results.order_by(
        order_col.asc() if direction == "asc" else order_col.desc())

    if total_pages == 0:
        items: List[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        items = db.execute(results.limit(per_page).offset(
            start)).scalars().all()  # [10,20]
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

# path parameters define an exact resource

# here it tales the response model that apply


@app.get("/post/{post_id}", response_model=Union[PostPublic, PostSummary], response_description="Post found")
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title="post id",
    description="identifies has to be grater that one",
    example=1
), include_content: bool = Query(default=True, description="discard content flag"),
        db: Session = Depends(get_db)):
    # look for id value indisde model in db

    post_find = select(PostORM).where(PostORM.id == post_id)
    post = db.execute(post_find).scalar_one_or_none()
    # post = db.get(PostORM, post_id)

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


@app.post("/posts", response_model=PostPublic, response_description="posts created", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):

    author_obj = None
    if post.author :
        author_obj = db.execute(select(AuthorORM).where(AuthorORM.email == post.author.email)
                                ).scalar_one_or_none()
        
        if not author_obj:
            author_obj = AuthorORM(name=post.author.name, email = post.author.email)
            
            db.add(author_obj)
            # secure it has an id
            db.flush()
            
    new_post = PostORM(title=post.title, content=post.content, author = author_obj)
    for tag in post.tags:
        tag_obj = db.execute(
            select(TagORM).where(TagORM.name.ilike(tag.name))
        ).scalar_one_or_none()
        if not tag_obj:
            tag_obj = TagORM(name = tag.name)
            # generate id
            db.add(tag_obj)
            db.flush()
            # sdd tag to the new post
        new_post.tags.append(tag_obj)
        
    try:
        # 1 insertin marking
        db.add(new_post)
        # confirm with a commit
        db.commit()
        #  bring the final values like id or created at
        db.refresh(new_post)
        return new_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="the title already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error creating the post")

    # new_id = (BLOCK_POST[-1]["id"]+1) if BLOCK_POST else 1
    # new_post = {"id": new_id,
    #             "title": post.title,
    #             "content": post.content,
    #             "tags": [tag.model_dump() for tag in post.tags],
    #             "author": post.author.model_dump() if post.author else None
    #             }
    # BLOCK_POST.append(new_post)
    # return new_post


@app.put("/post/{post_id}", response_model=PostPublic, response_description="post updated", response_model_exclude=None,)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    # obtain the post
    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="post not found")

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(post, key, value)

        db.add(post)
        # confirm with a commit
        db.commit()
        #  bring the final values like id or created at
        db.refresh(post)

        # for post in BLOCK_POST:
        #     if post["id"] == post_id:
        #         playload = data.model_dump(exclude_unset=True)
        #         if "title" in playload:
        #             post["title"] = playload["title"]
        #         if "content" in playload:
        #             post["content"] = playload["content"]
        #         return post
    return post
# for updates setattr()
#  for saving in db add(), commit(), db.refresh()


@app.delete("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="postid not found")

    db.delete(post)
    db.commit()

    return


# method to delete
