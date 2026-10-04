from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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
    # author: Optional[Author] = None

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

