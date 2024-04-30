import cloudinary
import cloudinary.uploader
<<<<<<< Updated upstream
from fastapi import Depends, UploadFile, File
=======
from fastapi import Depends, UploadFile, File, HTTPException
>>>>>>> Stashed changes
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from typing import List

from src.conf.config import config
from src.database.db import get_db
from src.entity.models import User, Photo
<<<<<<< Updated upstream
from src.schemas.user import UserSchema
from src.schemas.photo import PhotoSchema

=======
from src.schemas.photo import PhotoSchema
from src.repository.tags import create_or_get_tag
>>>>>>> Stashed changes

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


async def get_photo(email: str, db: AsyncSession = Depends(get_db)):
    """
    Get a user by email.

<<<<<<< Updated upstream
    :param email: str: Pass in the email of the user we want to get from our database
    :param db: AsyncSession: Connect to the database
    :return: A user object if the email exists in the database
=======
    :param email: str: The email of the user to get
    :param db: AsyncSession: The database session
    :return: User: The user object
>>>>>>> Stashed changes
    """
    filter_user = select(User).filter_by(email=email)
    user = await db.execute(filter_user)
    user = user.scalar_one_or_none()
    return user


async def get_photos(
    skip: int, limit: int, user: User, db: AsyncSession = Depends(get_db)
) -> List[Photo]:
    """
<<<<<<< Updated upstream
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
=======
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
>>>>>>> Stashed changes
    user: User,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(),
) -> Photo:
<<<<<<< Updated upstream
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
=======
    
    """
    Create a new photo in the database.

    :param body: PhotoSchema: The data from the request body
    :param user: User: The user creating the photo
    :param db: AsyncSession: The database session
    :param file: UploadFile: The file to upload
    :return: Photo: The created photo object
    """
    print(user)
    public_id = f"PhotoShare/{user.email}/{title}"
    res_photo = cloudinary.uploader.upload(
        file.file,
        public_id=public_id,
        overwrite=True)
    
>>>>>>> Stashed changes
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=300, height=300, crop="fill", version=res_photo.get("version")
    )
    photo = Photo(
<<<<<<< Updated upstream
        title=body.title, description=description, file_path=res_url, user_id=user.id
=======
        title=title, description=description, file_path=res_url, user_id=user.id
>>>>>>> Stashed changes
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def update_photo_description(
    photo_id: int, description: str, user: User, db: AsyncSession = Depends(get_db)
<<<<<<< Updated upstream
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
=======
) -> Photo:
   
    photo_expression = select(Photo).filter_by(id=photo_id, user_id=user.id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    photo.description = description
    await db.commit()
    await db.refresh(photo)
>>>>>>> Stashed changes
    return photo


async def remove_photo(
    photo_id: int, user: User, db: AsyncSession = Depends(get_db)
<<<<<<< Updated upstream
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
=======
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
    photo = db.query(Photo).filter_by(id=photo_id).one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo
>>>>>>> Stashed changes
