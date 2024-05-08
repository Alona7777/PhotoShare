from typing import List, Any, Dict
from fastapi import APIRouter, Depends, UploadFile, File, status, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Photo, PhotoTag
from src.schemas.photo import PhotoResponse, PhotoTagResponse
from src.schemas.qr_code import QRCodeResponse
from src.services.auth import auth_service
from src.repository import photos as repositories_photos
from src.repository import qr_code as repositories_qr_code
from src.repository import tags as repositories_tags


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
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :param : Get the id of a photo
    :return: A list of photos
    """
    photos = await repositories_photos.get_photos(skip, limit, current_user, db)
    output_photos = []
    for photo in photos:
        photo_obj: Photo = photo[0]
        output_photos.append(
            {
                "id": photo_obj.id,
                "title": photo_obj.title,
                "description": photo_obj.description,
                "file_path": photo_obj.file_path,
            }
        )
    return output_photos


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
    title: str = Form(),
    description: str | None = Form(),
    file: UploadFile = File(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
    """
    The create_photo function creates a new photo in the database.
    
    :param title: str: Get the title from the form
    :param description: str | None: Specify that the description field is optional
    :param file: UploadFile: Get the file from the request
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :param : Get the photo id from the url
    :return: A photo object, which is the same as what we defined in models
    """
    photo = await repositories_photos.create_photo(title, description, current_user, db, file)
    return photo


@router.put("/{photo_id}/{description}", response_model=PhotoResponse)
async def update_photo_description(
    description: str,
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
    """
    The update_photo_description function updates the description of a photo.
    
    :param description: str: Pass the new description of the photo to be updated
    :param photo_id: int: Identify the photo to update
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user
    :param : Get the photo id from the url
    :return: A photo object
    """
    photo = await repositories_photos.update_photo_description(
        photo_id, description, current_user, db
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
    
    :param photo_id: int: Identify the photo to be removed
    :param db: AsyncSession: Pass the database connection to the function
    :param current_user: User: Get the user that is currently logged in
    :param : Get the photo id from the request body
    :return: A photo object
    """
    photo = await repositories_photos.remove_photo(photo_id, current_user, db)
    return photo


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo_by_photo_id(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
    """
    The get_photo_by_photo_id function returns a photo object with the given id.
    
    :param photo_id: int: Get the photo by id
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :param : Get the photo_id from the url
    :return: A photo object
    """
    photo = await repositories_photos.get_photo_by_id(photo_id, current_user, db)
    # return {"id" : photo.id, "title" : photo.title, "description" : photo.description,
    #         "file_path" : photo.file_path}
    return photo


@router.post("/{photo_id}/qr", response_model=QRCodeResponse)
async def create_qr_code(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Dict[str, Any]:
    """
    The create_qr_code function creates a QR code from the photo's file_path.
        The function takes in a photo_id and returns the id of the photo and its qr code url.
    
    :param photo_id: int: Get the photo from the database
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the user who is currently logged in
    :param : Get the photo id from the request body
    :return: A dictionary with the photo id and file path of the qr code
    """
    photo = await repositories_photos.get_photo_by_id(photo_id, current_user, db)
    data = photo.file_path
    img_byte_arr = await repositories_qr_code.generate_qr_code(data)
    qr_url = await repositories_qr_code.upload_qr_to_cloudinary(
        img_byte_arr, f"{photo.title}"
    )
    return {"id": photo.id, "file_path": qr_url}



@router.post("/tag/{photo_id}", response_model=PhotoTagResponse)
async def create_tag_for_photo(
    photo_id: int,
    tag: str = Form(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> PhotoTag:
    photo = await repositories_photos.get_photo_by_id(photo_id, current_user, db)
    photo_title = photo.title
    photo_description = photo.description
    tags = await repositories_photos.create_tag_photo(photo_id, tag, db)
    photo_tags = {
            "id": photo_id,
            "title": photo_title,
            "description": photo_description,
            "tags": tags,
            }
    return photo_tags
 

