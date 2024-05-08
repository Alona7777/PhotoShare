from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role

from src.services.auth import auth_service
from src.services.roles import RoleAccess

from src.repository import photos as repositories_photos
from src.repository import transformation as repositories_transformations
from src.schemas.transformation import CropSchema, PhotoTransformResponse

router = APIRouter(prefix="/photos_transform", tags=["transforms"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PhotoTransformResponse,
    summary="Function to apply a transformation to a photo",
)
async def apply_transformation(
    body: CropSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> dict:
    """
     - **aspect_ratio** - float: The aspect ratio of the photo, 1 is square, 0.5 is landscape, 2 is portrait
    - **width** - int: The width of the photo
    - **is_rounded** - bool: If the photo should be rounded
    - **crop** - str: The crop type: fiill, scale, fit, limit, mfit, pad, crop, thumb, imagga_crop
    - **angle** - int: The angle of the photo in degrees, can be 0, 90, 180, 270 or -90, -180, -270
    - **effect** - str: The effect to apply to the photo, can be cartoonify, pixelate:5, vignette,  art:zorro, art:al_dente, art:audrey, art:eucalyptus, art:incognito, art:linen, art:peacock, art:red_rock, art:stucco
    """
    original_photo = await repositories_photos.get_photo_by_id(
        photo_id=body.id, user=current_user, db=db
    )
    return await repositories_transformations.create_crop_transformation(
        original_photo, body, db
    )
