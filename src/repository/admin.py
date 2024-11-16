import cloudinary
import cloudinary.uploader
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.conf.config import config
from src.conf import massages
from src.database.db import get_db
from src.entity.models import Photo, BanUser


cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


async def update_photo_description(
    photo_id: int, description: str, db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    The update_photo_description function updates the description of a photo.
        Args:
            photo_id (int): The id of the photo to update.
            description (str): The new description for the photo.
    
    :param photo_id: int: Identify the photo to update
    :param description: str: Pass the new description to the function
    :param db: AsyncSession: Get the database session
    :return: A photo object
    """
    photo_expression = select(Photo).filter_by(id=photo_id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=massages.NOT_PHOTO
        )
    photo.description = description
    await db.commit()
    await db.refresh(photo)
    return photo


async def remove_photo(photo_id: int, db: AsyncSession = Depends(get_db)) -> Photo:
    """
    The remove_photo function is used to remove a photo from the database.
        It takes in a photo_id and returns the removed Photo object.
    
    
    :param photo_id: int: Specify the id of the photo that will be removed
    :param db: AsyncSession: Pass the database session into the function
    :return: The removed photo
    """
    photo_expression = select(Photo).filter_by(id=photo_id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=massages.NOT_PHOTO
        )
    await db.delete(photo)
    await db.commit()
    return photo


async def get_photo_by_id(photo_id: int, db: AsyncSession = Depends(get_db)) -> Photo:
    """
    The get_photo_by_id function takes a photo_id and returns the corresponding Photo object.
    If no such photo exists, it raises an HTTPException with status code 404.
    
    :param photo_id: int: Get the photo id from the url
    :param db: AsyncSession: Pass the database session to the function
    :return: A photo object
    """
    photo_expression = select(Photo).filter_by(id=photo_id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=massages.NOT_PHOTO
        )
    return photo


async def create_ban_by_user_id(user_id: int, db: AsyncSession) -> BanUser:
    """
    The create_ban_by_user_id function creates a ban for the user with the given id.
        Args:
            user_id (int): The id of the user to be banned.
            db (AsyncSession): An async database session object.
    
    :param user_id: int: Specify the user id of the user to be banned
    :param db: AsyncSession: Pass the database session to the function
    :return: A banuser object
    """
    ban_user = BanUser(user_id=user_id)
    db.add(ban_user)
    await db.commit()
    await db.refresh(ban_user)
    return ban_user


async def delete_ban_by_user_id(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> BanUser:
    """
    The delete_ban_by_user_id function deletes a ban by user_id.
        Args:
            user_id (int): The id of the ban to delete.
    
    :param user_id: int: Find the user in the database
    :param db: AsyncSession: Get the database session
    :return: A banuser object
    """
    user_expression = select(BanUser).filter(BanUser.user_id == user_id)
    ban = await db.execute(user_expression)
    ban_user = ban.scalar_one_or_none()
    if not ban_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=massages.NOT_BAN_USER
        )
    await db.delete(ban_user)
    await db.commit()
    return ban_user


async def get_ban_users(
    skip: int, limit: int, db: AsyncSession = Depends(get_db)
) -> List[BanUser]:
    """
    The get_ban_users function returns a list of ban_users.
        The skip and limit parameters are used to paginate the results.
        
    
    :param skip: int: Skip the first n ban users
    :param limit: int: Limit the number of ban_users returned
    :param db: AsyncSession: Pass in the database session
    :return: A list of banuser objects
    """
    expression = select(BanUser).offset(skip).limit(limit)
    ban_users = await db.execute(expression)
    ban_users = ban_users.all()
    return ban_users


async def get_ban_by_user_id(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> BanUser | None:
    """
    The get_ban_by_user_id function takes in a user_id and returns the ban_user object associated with that user.
        If no such ban exists, it will return None.
    
    :param user_id: int: Filter the ban_user table by user_id
    :param db: AsyncSession: Pass the database session to the function
    :return: The ban_user object if it exists, or none if it doesn't
    """
    filter_user = select(BanUser).filter(BanUser.user_id == user_id)
    ban_user = await db.execute(filter_user)
    ban_user = ban_user.scalar_one_or_none()
    return ban_user
