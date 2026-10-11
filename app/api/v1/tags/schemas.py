from typing import Optional

from click import Option
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import desc


class TagPublic (BaseModel):
    id: int
    name: str = Field(
        ...,
        max_length=30,
        min_length=3,
        description="Tag name"
    )
    # here to receive objects not only dictionalt
    model_config = ConfigDict(from_attributes=True)

class TagCreate(BaseModel):
        name: str = Field(
            ...,
            min_length=2,
            max_length=30,
            description="Tag Name"
        )

class TagUpdate(BaseModel):

        name: Optional[str] = Field(
            ...,
            min_length=2,
            max_length=30,
            description="Tag Name"
        )

class TagWithCount(TagPublic):
        uses: int
