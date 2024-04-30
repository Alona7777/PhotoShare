import random
import string
import cloudinary
import cloudinary.uploader
from fastapi import Depends, UploadFile, File, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from typing import List

from src.conf.config import config
from src.database.db import get_db
from src.entity.models import User, Photo
from src.schemas.photo import PhotoSchema
from src.repository.tags import create_or_get_tag

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


async def get_photo(email: str, db: AsyncSession = Depends(get_db)):
    """
    Get a user by email.

    :param email: str: The email of the user to get
    :param db: AsyncSession: The database session
    :return: User: The user object
    """
    filter_user = select(User).filter_by(email=email)
    user = await db.execute(filter_user)
    user = user.scalar_one_or_none()
    return user


async def get_photos(
    skip: int, limit: int, user: User, db: AsyncSession = Depends(get_db)
) -> List[Photo]:
    """
    Get photos for a given user.

    :param skip: int: Skip a number of photos
    :param limit: int: Limit the number of photos returned
    :param user: User: The user to get photos for
    :param db: AsyncSession: The database session
    :return: List[Photo]: A list of photo objects
    """
    expression = select(Photo).filter_by(user_id = user.id).offset(skip).limit(limit)
    photos = await db.execute(expression)
    photos = photos.all()
    return photos


async def create_photo(
    title: str,
    description: str | None,
    user: User,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(),
) -> Photo:
    
    """
    Create a new photo in the database.

    :param body: PhotoSchema: The data from the request body
    :param user: User: The user creating the photo
    :param db: AsyncSession: The database session
    :param file: UploadFile: The file to upload
    :return: Photo: The created photo object
    """
    print(user)
    letters = string.ascii_lowercase
    random_name = ''.join(random.choice(letters) for _ in range(20))
    public_id = f"PhotoShare/{user.email}/{random_name}"
    res_photo = cloudinary.uploader.upload(
        file.file,
        public_id=public_id,
        overwrite=True)
    
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=300, height=300, crop="fill", version=res_photo.get("version")
    )
    photo = Photo(
        title=title, description=description, file_path=res_url, user_id=user.id
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def update_photo_description(
    photo_id: int, description: str, user: User, db: AsyncSession = Depends(get_db)
) -> Photo:
   
    photo_expression = select(Photo).filter_by(id=photo_id, user_id=user.id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    photo.description = description
    await db.commit()
    await db.refresh(photo)
    return photo


async def remove_photo(
    photo_id: int, user: User, db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    Remove a photo.

    :param photo_id: int: The id of the photo to remove
    :param user: User: The user removing the photo
    :param db: AsyncSession: The database session
    :return: Photo: The removed photo object
    """
    photo_expression = select(Photo).filter_by(id=photo_id, user_id=user.id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    await db.delete(photo)
    await db.commit()
    return photo


async def get_photo_by_id(
    photo_id: int, db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    Get a photo by its id.

    :param photo_id: int: The id of the photo to get
    :param db: AsyncSession: The database session
    :return: Photo: The photo object
    """
    photo = select(Photo).filter(Photo.id == photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo