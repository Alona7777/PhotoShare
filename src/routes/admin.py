from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, Form
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Photo, Role
from src.schemas.user import BanUser
from src.schemas.photo import PhotoResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf.config import config
from src.conf import messages
from src.repository import admin as repositories_admin
from src.repository import users as repositories_users
from src.repository import photos as repositories_photos

router = APIRouter(prefix="/admin", tags=["admin"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get(
    "/all/{user_id}",
    response_model=List[PhotoResponse],
    dependencies=[Depends(access_to_route_all)],
)
async def get_photos(
    user_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> List[Photo]:
    """
    The get_photos function returns a list of photos for the user with the given id.
    The function takes in an optional skip and limit parameter to paginate through results.
    
    
    :param user_id: int: Get the user
    :param skip: int: Skip the first n photos
    :param limit: int: Limit the number of photos returned
    :param db: AsyncSession: Pass a database session to the function
    :return: A list of dictionaries
    """
    user = await repositories_users.get_user_by_id(user_id, db)
    photos = await repositories_photos.get_photos(
        user=user, skip=skip, limit=limit, db=db
    )
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


@router.post(
    "/{user_id}",
    response_model=PhotoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_to_route_all)],
)
async def create_photo(
    user_id: int,
    title: str = Form(),
    description: str | None = Form(),
    file: UploadFile = File(),
    db: AsyncSession = Depends(get_db),
) -> Photo:
    """
    The create_photo function creates a new photo in the database.
    
    :param user_id: int: Get the user from the database
    :param title: str: Set the title of the photo
    :param description: str | None: Allow the description to be optional
    :param file: UploadFile: Receive the file from the client
    :param db: AsyncSession: Pass the database session to the repository
    :param : Get the user_id from the path
    :return: A photo object
    """
    user = await repositories_users.get_user_by_id(user_id, db)
    photo = await repositories_photos.create_photo(
        user=user, title=title, description=description, db=db, file=file
    )
    return photo


@router.put(
    "/{photo_id}/{description}",
    response_model=PhotoResponse,
    dependencies=[Depends(access_to_route_all)],
)
async def update_photo_description(
    description: str, photo_id: int, db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    The update_photo_description function updates the description of a photo.
        Args:
            description (str): The new description for the photo.
            photo_id (int): The id of the photo to update.
    
    :param description: str: Get the description of a photo
    :param photo_id: int: Identify the photo to update
    :param db: AsyncSession: Pass the database session to the function
    :return: The updated photo
    """
    photo = await repositories_admin.update_photo_description(photo_id, description, db)
    return photo


@router.delete(
    "/{photo_id}",
    response_model=PhotoResponse,
    dependencies=[Depends(access_to_route_all)],
)
async def remove_photo(photo_id: int, db: AsyncSession = Depends(get_db)) -> Photo:
    """
    The remove_photo function removes a photo from the database.
        Args:
            photo_id (int): The id of the photo to be removed.
            db (AsyncSession, optional): An async session object for interacting with the database. Defaults to Depends(get_db).
    
    :param photo_id: int: Specify the photo to be removed
    :param db: AsyncSession: Get the database session
    :return: The removed photo
    """
    photo = await repositories_admin.remove_photo(photo_id, db)
    return photo


@router.get(
    "/{photo_id}",
    response_model=PhotoResponse,
    dependencies=[Depends(access_to_route_all)],
)
async def get_photo_by_photo_id(
    photo_id: int, db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    The get_photo_by_photo_id function returns a photo object with the given id.
        If no photo is found, it raises an HTTPException with status 404 (Not Found).
    
    
    :param photo_id: int: Specify the photo id of the photo we want to delete
    :param db: AsyncSession: Pass the database session to the function
    :return: A photo object
    """
    photo = await repositories_admin.get_photo_by_id(photo_id, db)
    # return {"id" : photo.id, "title" : photo.title, "description" : photo.description,
    #         "file_path" : photo.file_path}
    return photo


@router.post(
    "/ban_user/{user_id}",
    response_model=BanUser,
    dependencies=[
        Depends(RateLimiter(times=1, seconds=60)),
        Depends(access_to_route_all),
    ],
)
async def create_ban_for_user(
    user_id: int,
    user_admin: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BanUser:
    """
    The create_ban_for_user function creates a ban for the user with the given id.
        The function takes in an integer representing the user_id of the user to be banned,
        and returns a BanUser object containing information about that ban.
    
    :param user_id: int: Get the user id from the url
    :param user_admin: User: Get the current user
    :param db: AsyncSession: Create a database connection
    :param : Get the current user
    :return: A banuser object
    """
    user = await repositories_users.get_user_by_id(user_id=user_id, db=db)
    if user.id == user_admin.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.CONFLICT_ROLE
        )
    ban_user = await repositories_admin.create_ban_by_user_id(user_id=user_id, db=db)
    return ban_user


@router.delete(
    "/ban_user/{user_id}",
    response_model=BanUser,
    dependencies=[
        Depends(RateLimiter(times=1, seconds=30)),
        Depends(access_to_route_all),
    ],
)
async def delete_user_from_ban(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> BanUser:
    """
    The delete_user_from_ban function deletes a user from the ban list.
        Args:
            user_id (int): The id of the banned user to be deleted.
    
    :param user_id: int: Get the user_id from the request body
    :param db: AsyncSession: Get the database session
    :return: The deleted user
    """
    ban_user = await repositories_admin.delete_ban_by_user_id(user_id, db)
    return ban_user


@router.get(
    "/ban_users/all",
    response_model=List[BanUser],
    dependencies=[Depends(access_to_route_all)],
)
async def ban_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> List[BanUser]:
    """
    The ban_users function returns a list of banned users.
    
    :param skip: int: Skip the first n users in the database
    :param limit: int: Limit the number of users returned
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of ban_users
    """
    ban_users = await repositories_admin.get_ban_users(skip, limit, db)
    output_users = []
    for user in ban_users:
        ban_user: BanUser = user[0]
        output_users.append({"id": ban_user.id, "user_id": ban_user.user_id})
    return output_users
