import pickle

import cloudinary
import cloudinary.uploader

from typing import List
<<<<<<< Updated upstream
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
=======
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, Form
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/all/", response_model=List[PhotoResponse])
async def get_photos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> List[Photo]:
<<<<<<< Updated upstream
    """
    The read_contacts function returns a list of contacts.

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A list of contacts, which is the same type as the contact class
    :doc-author: Trelent
    """
    photos = await repositories_photos.get_photos(skip, limit, current_user, db)
    return photos
=======

    photos = await repositories_photos.get_photos(skip, limit, current_user, db)
    output_photos = []
    for photo in photos:
        photo_obj: Photo = photo[0]
        output_photos.append({"id": photo_obj.id, "title": photo_obj.title, "description": photo_obj.description,
                             "file_path": photo_obj.file_path })
    return output_photos
>>>>>>> Stashed changes


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
<<<<<<< Updated upstream
    body: PhotoSchema,
=======
    title:str = Form(),
    description: str | None = Form(),

>>>>>>> Stashed changes
    file: UploadFile = File(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
<<<<<<< Updated upstream
    """
    The create_photo function creates a new photo in the database.

    :param body: PhotoSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the repository
    :param current_user: User: Get the user from the database
    :param : Get the photo id from the url
    :return: A photo object, which is defined in the models/photos
    :doc-author: Alona Boholiepova
    """
    return await repositories_photos.create_photo(body, file, current_user, db)
=======
    

    return await repositories_photos.create_photo(title, description, current_user, db, file)
>>>>>>> Stashed changes


@router.put("/{photo_id}/{description}", response_model=PhotoResponse)
async def update_photo_description(
    description: str,
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
<<<<<<< Updated upstream
    """
    The update_photo_description function updates the description of a photo.
        Args:
            description (str): The new description for the photo.
            photo_id (int): The id of the photo to update.

    :param description: str: Get the description of the photo
    :param photo_id: int: Get the photo id from the url
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :param : Get the photo id from the url
    :return: The updated photo
    :doc-author: Alona Boholiepova
    """
=======
   
>>>>>>> Stashed changes
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
