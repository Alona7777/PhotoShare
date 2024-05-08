from enum import Enum
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PhotoRating(str, Enum):
    one_star = 'Very bad'
    two_stars = 'Bad'
    three_stars = 'Average'
    four_stars = 'Good'
    five_stars = 'Excellent'


class ViewPhotoRating(BaseModel):
    id: int
    user_id: int
    photo_id: int
    rating: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuantityRating(BaseModel):
    number_of_ratings: int
    VeryBad: int
    Bad: int
    Average: int
    Good: int
    Excellent: int
    average_rating: float

    model_config = ConfigDict(from_attributes=True)


class RatingModel(BaseModel):
    id: int
    rating: int

    model_config = ConfigDict(from_attributes=True)
