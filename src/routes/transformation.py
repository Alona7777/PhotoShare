import pickle

import cloudinary
import cloudinary.uploader

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, Form
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Photo, Role
from src.schemas.user import UserResponse
from src.schemas.photo import PhotoResponse, PhotoSchema
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf.config import config
from src.conf import messages
from src.repository import photos as repositories_photos
from src.repository import transformation as repositories_transformations
from src.schemas.transformation import CropSchema

router = APIRouter(prefix = "/photos_transform", tags = ["transforms"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])

@router.post("/", status_code = status.HTTP_201_CREATED, response_model=None) #response_model = PhotoResponse
async def apply_transformation(
    body: CropSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Photo :
    original_photo = await repositories_photos.get_photo_by_ID( photo_id=body.id,user=current_user,
                                                               db=db)
    if original_photo is None :
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, detail = messages.NOT_FOUND
        )
    trans_photo = await repositories_transformations.create_crop_transformation(original_photo,body, current_user)
