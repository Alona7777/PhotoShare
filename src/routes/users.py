import pickle

import cloudinary
import cloudinary.uploader

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, BanUser
from src.schemas import user as schemas_user
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users
from src.services.roles import RoleAccess, Role
from src.conf import messages


router = APIRouter(prefix = "/users", tags = ["users"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model = schemas_user.UserResponse,
    dependencies = [Depends(RateLimiter(times = 1, seconds = 20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Get the current user
    :return: The current user object, which is the user model
    :doc-author: Naboka Artem
    """
    return user


@router.get(
    "/user/{id}",
    response_model = schemas_user.UserResponseAll,
    dependencies = [Depends(RateLimiter(times = 1, seconds = 20))],
)
async def get_user_info(user: User = Depends(auth_service.get_user_info)) -> User:
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param id:
    :param user: User: Get the current user
    :return: The current user object, which is the user model
    :doc-author: Naboka Artem
    """
    return user


@router.patch(
    "/avatar",
    response_model = schemas_user.UserResponse,
    dependencies = [Depends(RateLimiter(times = 1, seconds = 20))],
)
async def get_current_user(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    The get_current_user function is a dependency that returns the current user.
    It uses the auth_service to get it from the Authorization header, and then
    it gets it from cache or database.

    :param file: UploadFile: Get the uploaded file from the client
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Get the database session
    :param : Get the current user from the database
    :return: The current user, based on the token in the authorization header
    :doc-author: Naboka Artem
    """
    public_id = f"Web19_fastapi/{user.email}"
    res_photo = cloudinary.uploader.upload(file.file, public_id = public_id, owerite = True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width = 300, height = 300, crop = "fill", version = res_photo.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user

@router.get(
    "/ban_user/{id}",
    response_model = schemas_user.BanUser,
    dependencies = [Depends(RateLimiter(times = 1, seconds = 60)), Depends(access_to_route_all)]

)
async def create_ban_by_user_id(user_id: int, user_admin: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)) -> BanUser:
    user = await repositories_users.get_user_by_id(user_id=user_id, db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND
        )
    if user.id == user_admin.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.CONFLICT_ROLE
        )
    ban_user = await repositories_users.create_ban_by_user_id(user_id=user_id, db=db)
    return ban_user

@router.delete(
    "/ban_user/{user_id}",
    response_model = schemas_user.BanUser,
    dependencies = [Depends(RateLimiter(times = 1, seconds = 30)), Depends(access_to_route_all)],

)
async def delete_ban_by_user_id(user_id: int, db: AsyncSession = Depends(get_db)) -> BanUser:
    ban_user = await repositories_users.delete_ban_by_user_id(user_id, db)
    return ban_user


@router.get(
    "/all/ban_users",
    response_model = List[schemas_user.BanUser],
    dependencies = [Depends(access_to_route_all)],

)
async def ban_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> List[BanUser]:
    ban_users = await repositories_users.get_ban_users(skip, limit, db)
    output_users = []
    for user in ban_users:
        ban_user: BanUser = user[0]
        output_users.append({"id": ban_user.id, "user_id": ban_user.user_id})
    return output_users

