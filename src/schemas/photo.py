import enum
from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.schemas.tag import TagResponse


# from src.schemas.user import UserResponse


class PhotoSchema(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str | None = ""
    tags: List[str]
    # file_path: str


class PhotoResponse(BaseModel):
    id: int = 1
    title: str
    description: str
    file_path: str

    model_config = ConfigDict(from_attributes=True)


class PhotoTagResponse(BaseModel):
    id: int = 1
    title: str
    description: str
    tags: List[str]

    model_config = ConfigDict(from_attributes=True)


class SortDirection(enum.Enum):
    asc = 'asc'
    desc = 'desc'


class CommentModel(BaseModel):
    content: str = Field(max_length=2000)


class CommentResponse(CommentModel):
    id: int
    content: str = Field(max_length=2000)
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
