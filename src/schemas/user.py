from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.entity.models import Role


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=5, max_length=10)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: str | None
    
    # count_photo: int | None
    count_photo: Optional[int] = None
    # count_comment: int | None
    count_comment: Optional[int] = None
    # count_rating: int | None
    count_rating: Optional[int] = None
    # count_friendship: int | None
    count_friendship: Optional[int] = None
    role: Role

    model_config = ConfigDict(from_attributes = True)


class UserResponseAll(BaseModel):
    id: int = 1
    username: str
    avatar: str
    count_photo: int
    count_comment: int
    count_rating: int
    count_friendship: int
    role: Role

    model_config = ConfigDict(from_attributes = True)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    password1: str
    password2: str
