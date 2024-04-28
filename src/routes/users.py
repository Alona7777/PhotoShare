import pickle

import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix = "/users", tags = ["users"])

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model = UserResponse,
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


@router.patch(
    "/avatar",
    response_model = UserResponse,
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
    # print(res_photo)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width = 300, height = 300, crop = "fill", version = res_photo.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
