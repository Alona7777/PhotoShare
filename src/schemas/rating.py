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
    user_id: int = Field(1, gt=0)
    image_id: int = Field(1, gt=0)


class RatingResponse(BaseModel):
    id: int = 1
    rating: dict = {"one_star": False, "two_stars": False, "three_stars": False, "four_stars": False,
                    "five_stars": False}
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)
