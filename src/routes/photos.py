import pickle

import cloudinary
import cloudinary.uploader

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, Form
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Photo
from src.schemas.user import UserResponse
from src.schemas.photo import PhotoResponse, PhotoSchema
from src.services.auth import auth_service
from src.conf.config import config
from src.conf import messages
from src.repository import photos as repositories_photos

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/all/", response_model=List[PhotoResponse])
async def get_photos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> List[Photo]:
    """
    The get_photos function returns a list of photos.
    
    :param skip: int: Skip the first n photos
    :param limit: int: Limit the number of photos returned
    :param db: AsyncSession: Pass the database connection to the function
    :param current_user: User: Pass the current user to the get_photos function
    :param : Get the id of the photo to be deleted
    :return: A list of photos
    """
    photos = await repositories_photos.get_photos(skip, limit, current_user, db)
    output_photos = []
    for photo in photos:
        photo_obj: Photo = photo[0]
        output_photos.append({"id": photo_obj.id, "title": photo_obj.title, "description": photo_obj.description,
                             "file_path": photo_obj.file_path })
    return output_photos


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
    title:str = Form(),
    description: str | None = Form(),

    file: UploadFile = File(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
    """
    The create_photo function creates a new photo in the database.
        It takes in a title, description, and file as arguments.
        The function returns the newly created photo.
    
    :param title:str: Get the title of the photo from the request body
    :param description: str | None: Indicate that the description is optional
    :param file: UploadFile: Get the file from the request
    :param db: AsyncSession: Get a database session
    :param current_user: User: Get the user who is currently logged in
    :param : Get the current user
    :return: A photo object
    """
    return await repositories_photos.create_photo(title, description, current_user, db, file)


@router.put("/{photo_id}/{description}", response_model=PhotoResponse)
async def update_photo_description(
    description: str,
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
    """
    The update_photo_description function updates the description of a photo.
    
    :param description: str: Get the description from the request body
    :param photo_id: int: Get the photo id
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user who is making the request
    :param : Get the photo id
    :return: A photo object
    """
    photo = await repositories_photos.update_photo_description(
        photo_id, description, current_user, db
    )
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND
        )
    return photo


@router.delete("/{photo_id}", response_model=PhotoResponse)
async def remove_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
    """
    The remove_photo function is used to remove a photo from the database.
        The function takes in an integer representing the id of the photo to be removed,
        and returns a Photo object containing information about that photo.
    
    :param photo_id: int: Get the photo id from the url
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :param : Get the photo id from the url
    :return: The removed photo
    """
    photo = await repositories_photos.remove_photo(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND
        )
    return photo


# @router.patch(
#     "/photo",
#     response_model=PhotoResponse,
#     dependencies=[Depends(RateLimiter(times=1, seconds=20))],
# )
# async def get_current_photo(
#     body: PhotoSchema,
#     file: UploadFile = File(),
#     user: User = Depends(auth_service.get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     """
#     The get_current_user function is a dependency that returns the current user.
#     It uses the auth_service to get it from the Authorization header, and then
#     it gets it from cache or database.

#     :param body:
#     :param file: UploadFile: Get the uploaded file from the client
#     :param user: User: Get the current user from the database
#     :param db: AsyncSession: Get the database session
#     :param : Get the current user from the database
#     :return: The current user, based on the token in the authorization header
#     :doc-author: Naboka Artem
#     """
#     title = body.title
#     description = body.description
#     name_photo = title
#     public_id = f"Web19_fastapi/{user.email}/{name_photo}"
#     res_photo = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
#     # print(res_photo)
#     res_url = cloudinary.CloudinaryImage(public_id).build_url(
#         width=300, height=300, crop="fill", version=res_photo.get("version")
#     )
#     user = await repositories_users.update_avatar_url(user.email, res_url, db)
#     auth_service.cache.set(user.email, pickle.dumps(user))
#     auth_service.cache.expire(user.email, 300)
#     return user
