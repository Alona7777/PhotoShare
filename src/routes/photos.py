import pickle

import cloudinary
import cloudinary.uploader

from typing import Any

from typing import List, Dict
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, Form
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.base import _T_co

from src.database.db import get_db
from src.entity.models import User, Photo, Role
from src.schemas.user import UserResponse
from src.schemas.photo import PhotoResponse, PhotoSchema
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf.config import config
from src.conf import messages
from src.repository import photos as repositories_photos

router = APIRouter(prefix="/photos", tags=["photos"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/all/", response_model=List[PhotoResponse])
async def get_photos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> List[Photo]:

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

    return await repositories_photos.create_photo(
        title, description, current_user, db, file
    )


@router.put(
    "/{photo_id}/{description}",
    response_model=PhotoResponse,
    dependencies=[Depends(access_to_route_all)],
)
async def update_photo_description(
    description: str,
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo:

    photo = await repositories_photos.update_photo_description(
        photo_id, description, current_user, db
    )
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND
        )
    return photo


@router.delete(
    "/{photo_id}",
    response_model=PhotoResponse,
    dependencies=[Depends(access_to_route_all)],
)
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


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo_by_photoID(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> dict[str, Any]:
    photo = await repositories_photos.get_photo_by_ID(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND
        )
    return {
        "id": photo.id,
        "title": photo.title,
        "description": photo.description,
        "file_path": photo.file_path,
    }
