from typing import List, Sequence, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy import and_, select, func

from src.entity.models import Rating, User, Photo
from src.schemas.rating import RatingModel, PhotoRating, QuantityRating
from src.database.db import get_db

DICT_WITH_STARS = {"one_star" : 1, "two_stars" : 2, "three_stars" : 3, "four_srats" : 4, "five_stars" : 5}


async def create_rating_for_photo(photo_id: int,
                                  select_rating: PhotoRating,
                                  user: User,
                                  db: AsyncSession = Depends(get_db),
                                  ) -> Rating :
    count_rating = 0
    if select_rating == PhotoRating.one_star :
        count_rating = 1
    elif select_rating == PhotoRating.two_stars :
        count_rating = 2
    elif select_rating == PhotoRating.three_stars :
        count_rating = 3
    elif select_rating == PhotoRating.four_stars :
        count_rating = 4
    elif select_rating == PhotoRating.five_stars :
        count_rating = 5

    photo_expression = select(Photo).filter_by(id=photo_id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo :
        raise HTTPException(status_code=404, detail="Photo not found!")

    result = await db.execute(select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user.id))
    existing_rating = result.scalar_one_or_none()

    # Если рейтинг уже существует, возвращаем обновляем существующий рейтинг
    if existing_rating :
        existing_rating.rating = count_rating
        db.add(existing_rating)
        await db.commit()
        await db.refresh(existing_rating)
        return existing_rating
    else :
        # Создаем новый рейтинг
        new_rating = Rating(user_id=user.id, photo_id=photo_id,
                            rating=count_rating)
        db.add(new_rating)
        await db.commit()
        await db.refresh(new_rating)
        return new_rating


async def get_average_rating(image_id: int, db: AsyncSession) -> QuantityRating :
    result = await db.execute(select(Rating).where(Rating.photo_id == image_id))
    ratings = result.scalars().all()
    if not ratings :
        # Возвращаем пустой объект QuantityRating, если нет оценок
        return QuantityRating(
            number_of_ratings=0,
            VeryBad=0,
            Bad=0,
            Average=0,
            Good=0,
            Excellent=0,
            average_rating=0
        )

    number_of_ratings = len(ratings)
    total_rating = sum(rating.rating for rating in ratings)
    average_rating = total_rating / number_of_ratings

    # Count ratings distribution
    very_bad = sum(1 for rating in ratings if rating.rating == 1)
    bad = sum(1 for rating in ratings if rating.rating == 2)
    average = sum(1 for rating in ratings if rating.rating == 3)
    good = sum(1 for rating in ratings if rating.rating == 4)
    excellent = sum(1 for rating in ratings if rating.rating == 5)

    return QuantityRating(
        number_of_ratings=number_of_ratings,
        VeryBad=very_bad,
        Bad=bad,
        Average=average,
        Good=good,
        Excellent=excellent,
        average_rating=average_rating
    )


async def get_rating(photo_id: int,
                     user: User,
                     db: AsyncSession = Depends(get_db),
                     ) -> Rating :
    result = await db.execute(select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user.id))
    photo = result.scalar_one_or_none()
    if not photo :
        raise HTTPException(status_code=404, detail="Photo not found!")
    return photo


async def get_rating_id(rating_id: int,
                        db: AsyncSession = Depends(get_db),
                        ) -> Rating :
    result = await db.execute(select(Rating).where(Rating.id == rating_id))
    rating = result.scalar_one_or_none()
    if not rating :
        raise HTTPException(status_code=404, detail="Rating not found!")
    return rating


async def remove_rating(photo_id: int,
                        user: User,
                        db: AsyncSession = Depends(get_db),
                        ) :
    result = await db.execute(select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user.id))
    photo = result.scalar_one_or_none()
    if not photo :
        raise HTTPException(status_code=404, detail="Photo not found!")
    await db.delete(photo)
    await db.commit()
    return photo
