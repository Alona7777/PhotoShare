import enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SortDirection(enum.Enum):
    asc = 'asc'
    desc = 'desc'


class CommentModel(BaseModel):
    comment: str = Field(max_length=2000)


class CommentResponse(CommentModel):
    id: int
    comment: str = Field(max_length=2000)
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
