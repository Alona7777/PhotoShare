import cloudinary
import cloudinary.uploader
from fastapi import Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from typing import List

from src.conf.config import config
from src.database.db import get_db
from src.entity.models import User, Photo
from src.schemas.user import UserSchema
from src.schemas.photo import PhotoSchema


cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


async def get_photo(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no user is found, None is returned.

    :param email: str: Pass in the email of the user we want to get from our database
    :param db: AsyncSession: Connect to the database
    :return: A user object if the email exists in the database
    """
    filter_user = select(User).filter_by(email=email)
    user = await db.execute(filter_user)
    user = user.scalar_one_or_none()
    return user


async def get_photos(
    skip: int, limit: int, user: User, db: AsyncSession = Depends(get_db)
) -> List[Photo]:
    """
    The get_photos function returns a list of photos for the given user.

    :param skip: int: Skip a number of photos
    :param limit: int: Limit the number of photos returned
    :param user: User: Get the user from the database
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of photo objects
    """
    return (
        db.query(Photo).filter(Photo.user_id == user.id).offset(skip).limit(limit).all()
    )


async def create_photo(
    body: PhotoSchema,
    user: User,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(),
) -> Photo:
    """
    The create_photo function creates a new photo in the database.
        It takes a PhotoSchema object, which is used to create the new photo.
        The user who created this photo is also passed in as an argument, and their id is stored with the newly created Photo object.

    :param body: PhotoSchema: Get the data from the request body
    :param user: User: Get the user that is currently logged in
    :param db: AsyncSession: Get the database session
    :param file: UploadFile: Receive the file from the request
    :return: A photo object
    """
    description = None
    if body.description:
        description = body.description
    public_id = f"PhotoShare/{user.email}/{body.title}"
    res_photo = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=300, height=300, crop="fill", version=res_photo.get("version")
    )
    photo = Photo(
        title=body.title, description=description, file_path=res_url, user_id=user.id
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def update_photo_description(
    photo_id: int, description: str, user: User, db: AsyncSession = Depends(get_db)
) -> Photo | None:
    """
    The update_photo_description function updates the description of a photo.
        The function takes in three parameters:
            - photo_id: int, the id of the photo to update.
            - description: str, the new description for this photo.
            - user: User object, used to verify that this user is allowed to update this particular image's information.

    :param photo_id: int: Specify the photo to update
    :param description: str: Pass the new description to the function
    :param user: User: Ensure that the user is logged in and has access to the photo
    :param db: AsyncSession: Pass the database session to the function
    :return: The photo object after it has been updated
    """
    photo = db.query(Photo).filter_by(id=photo_id, user_id=user.id).one_or_none()
    if photo:
        photo.description = description
        await db.commit()
        await db.refresh(photo)
    return photo


async def remove_photo(
    photo_id: int, user: User, db: AsyncSession = Depends(get_db)
) -> Photo | None:
    """
    The remove_photo function takes a photo_id and user object as parameters.
    It then queries the database for a Photo with the given id and user_id, returning None if no such Photo exists.
    If it does exist, it deletes that photo from the database and commits those changes to the db.

    :param photo_id: int: Specify the id of the photo to be deleted
    :param user: User: Get the user object from the database
    :param db:AsyncSession: Pass in the database session
    :return: The deleted photo or none if no photo was found
    """
    photo = db.query(Photo).filter_by(id=photo_id, user_id=user.id).one_or_none()
    if photo:
        await db.delete(photo)
        await db.commit()
    return photo
