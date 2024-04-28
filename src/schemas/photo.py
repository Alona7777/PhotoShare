from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

# from src.schemas.user import UserResponse


class PhotoSchema(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=50)
    file_path: str


class PhotoResponse(BaseModel):
    id: int = 1
    title: str
    description: str
    file_path: str

    model_config = ConfigDict(from_attributes = True)
