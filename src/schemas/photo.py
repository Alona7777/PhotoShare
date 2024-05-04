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
    tags: List[TagResponse]

    model_config = ConfigDict(from_attributes=True)
