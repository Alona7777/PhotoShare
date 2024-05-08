from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from src.entity.models import Rating, User, Photo
from src.schemas.rating import PhotoRating, QuantityRating
from src.repository import admin as repositories_admin
from src.database.db import get_db
from src.conf import messages

DICT_WITH_STARS = {
    "one_star": 1,
    "two_stars": 2,
    "three_stars": 3,
    "four_stars": 4,
    "five_stars": 5,
}


async def create_rating_for_photo(
    photo_id: int,
    select_rating: PhotoRating,
    user: User,
    db: AsyncSession = Depends(get_db),
) -> Rating:
    """
    The create_rating_for_photo function creates a new rating for the photo with the given id.
    The function takes in an integer representing the photo's id, a PhotoRating enum value representing
    the user's rating of that photo, and an instance of User representing who is creating this rating.
    It returns an instance of Rating containing information about this newly created rating.
    
    :param photo_id: int: Get the photo that we want to rate
    :param select_rating: PhotoRating: Determine what rating the user is giving to a photo
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Pass the database session to the function
    :param : Get the photo id
    :return: A rating object
    """
    count_rating = 0
    if select_rating == PhotoRating.one_star:
        count_rating = 1
    elif select_rating == PhotoRating.two_stars:
        count_rating = 2
    elif select_rating == PhotoRating.three_stars:
        count_rating = 3
    elif select_rating == PhotoRating.four_stars:
        count_rating = 4
    elif select_rating == PhotoRating.five_stars:
        count_rating = 5

    photo_expression = select(Photo).filter_by(id=photo_id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_PHOTO)

    result = await db.execute(
        select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user.id)
    )
    existing_rating = result.scalar_one_or_none()
    if existing_rating:
        existing_rating.rating = count_rating
        db.add(existing_rating)
        await db.commit()
        await db.refresh(existing_rating)
        return existing_rating
    else:
        new_rating = Rating(user_id=user.id, photo_id=photo_id, rating=count_rating)
        db.add(new_rating)
        await db.commit()
        await db.refresh(new_rating)
        return new_rating


async def get_average_rating(image_id: int, db: AsyncSession) -> QuantityRating:
    """
    The get_average_rating function takes in an image_id and a database connection.
    It then queries the Rating table for all ratings associated with that image_id.
    If there are no ratings, it returns a QuantityRating object with 0 values for everything.
    Otherwise, it calculates the average rating by summing up all of the individual ratings and dividing by their number.  It also counts how many times each rating was given (VeryBad, Bad, Average...)
    
    :param image_id: int: Specify the image that we want to get the average rating for
    :param db: AsyncSession: Pass the database connection to the function
    :return: A quantityrating object
    """
    result = await db.execute(select(Rating).where(Rating.photo_id == image_id))
    ratings = result.scalars().all()
    if not ratings:
        return QuantityRating(
            number_of_ratings=0,
            VeryBad=0,
            Bad=0,
            Average=0,
            Good=0,
            Excellent=0,
            average_rating=0,
        )

    number_of_ratings = len(ratings)
    total_rating = sum(rating.rating for rating in ratings)
    average_rating = total_rating / number_of_ratings

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
        average_rating=average_rating,
    )


async def get_rating(
    photo_id: int,
    user: User,
    db: AsyncSession = Depends(get_db),
) -> Rating:
    """
    The get_rating function returns a Rating object for the given photo_id and user.
    
    :param photo_id: int: Get the photo id from the request url
    :param user: User: Get the user id from the token
    :param db: AsyncSession: Get the database session from the dependency
    :param : Get the photo id from the url
    :return: A rating object
    """
    result = await db.execute(
        select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user.id)
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_PHOTO)
    return photo


async def get_rating_id(
    rating_id: int,
    db: AsyncSession = Depends(get_db),
) -> Rating:
    """
    The get_rating_id function takes a rating_id and returns the Rating object with that id.
    If no such Rating exists, it raises an HTTPException with status code 404.
    
    :param rating_id: int: Get the rating id from the url
    :param db: AsyncSession: Get the database session from the dependency
    :param : Get the rating id from the database
    :return: A rating object
    """
    result = await db.execute(select(Rating).where(Rating.id == rating_id))
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_RATING)
    return rating


async def remove_rating(
    photo_id: int,
    user: User,
    db: AsyncSession = Depends(get_db),
):
    """
    The remove_rating function removes a rating from the database.
    
    :param photo_id: int: Identify the photo to be deleted
    :param user: User: Get the user id from the token
    :param db: AsyncSession: Pass the database connection to the function
    :param : Get the photo id from the url
    :return: The photo that was deleted
    """
    result = await db.execute(
        select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user.id)
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_PHOTO)
    await db.delete(photo)
    await db.commit()
    return photo
