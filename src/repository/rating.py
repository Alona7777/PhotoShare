from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from src.entity.models import Rating, User
from src.schemas.rating import RatingModel

DICT_WITH_STARS = {"one_star": 1, "two_stars": 2, "three_stars": 3, "four_srats": 4, "five_stars": 5}


async def get_average_rating(image_id: int, db: AsyncSession) -> float:
    result = await db.execute(select(Rating).where(Rating.photo_id == image_id))
    ratings = result.scalars().all()
    if not ratings:
        return 0
    sum_user_rating = sum(rating.rating for rating in ratings)
    average_user_rating = sum_user_rating / len(ratings)
    return average_user_rating


async def get_rating(rating: int, db: AsyncSession) -> Rating:
    stmt = select(Rating).where(Rating.id == rating)
    result = await db.execute(stmt)
    rating = result.scalars().first()
    return rating


async def create_rating_from_user(photo_id, body: RatingModel, user: User, db: AsyncSession) -> Rating | None:
    if user.id == body.user_id:
        return None
    result = await db.execute(select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == body.user_id))
    rating_in_database = result.scalars().first()
    if rating_in_database:
        return None
    rating_from_user = Rating(photo_id=photo_id, user_id=user.id, rating=body.rating)
    db.add(rating_from_user)
    await db.commit()
    await db.refresh(rating_from_user)
    return rating_from_user


async def update_rating(rating_id: int, body: RatingModel, db: AsyncSession) -> Rating | None:
    result = await db.execute(select(Rating).where(Rating.id == rating_id))
    rating = result.scalars().first()
    if rating:
        rating.rating = body.rating
        await db.commit()
    return rating


async def remove_rating(rating_id: int, db: AsyncSession) -> Rating | None:
    result = await db.execute(select(Rating).where(Rating.id == rating_id))
    rating = result.scalars().first()
    if rating:
        await db.delete(rating)
        await db.commit()

    return rating
