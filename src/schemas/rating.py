from pydantic import BaseModel, Field, ConfigDict
from typing import Dict

from src.schemas.user import UserResponse


class ViewRatingModel(BaseModel):
    one_star: bool
    two_stars: bool
    three_stars: bool
    four_stars: bool
    five_stars: bool


class RatingModel(BaseModel):
    rating: ViewRatingModel
    user_id: int = Field(..., gt=0)
    image_id: int = Field(..., gt=0)


class RatingResponse(BaseModel):
    id: int = 1
    rating: ViewRatingModel
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)
