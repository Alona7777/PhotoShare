from typing import List, Sequence, Dict, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.services.roles import RoleAccess
from src.database.db import get_db
from src.entity.models import User, Role, Rating
from src.schemas.rating import RatingModel, RatingResponse, PhotoRating, ViewPhotoRating
from src.repository import rating as repository_ratings
# from src.conf.messages import me

from src.services.auth import auth_service

router = APIRouter(prefix='/ratings', tags=["ratings"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.post("/photo/{photo_id}", description='Add photo rating!', response_model=ViewPhotoRating,
             status_code=status.HTTP_201_CREATED)
async def create_photo_rating(
        photo_id: int = Path(ge=1),
        select_rating: PhotoRating = PhotoRating.five_stars,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
) -> Optional[Rating] :
    add_rating = await repository_ratings.create_rating_for_photo(photo_id, select_rating, current_user, db)
    return add_rating


@router.get("/photo/{image_id}", response_model=int, dependencies=[Depends(access_to_route_all)])
async def get_common_rating(image_id: int, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)) :
    tags = await repository_ratings.get_average_rating(image_id, db)
    return tags


@router.get("/{rating_id}", response_model=RatingResponse, dependencies=[Depends(access_to_route_all)])
async def read_tag(rating_id: int, db: AsyncSession = Depends(get_db)) :
    rating = await repository_ratings.get_rating(rating_id, db)
    if rating is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return rating


@router.put("/{photo_id}", description='Update photo rating!', response_model=ViewPhotoRating)
async def update_rating(photo_id: int = Path(ge=1),
                        select_rating: PhotoRating = PhotoRating.five_stars,
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)
                        ) -> Optional[Rating] :
    rating = await repository_ratings.create_rating_for_photo(photo_id, select_rating, current_user, db)
    return rating


@router.delete("/{photo_id}", description='Delete photo rating!', dependencies=[Depends(access_to_route_all)],
               )
async def remove_rating(photo_id: int, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    rating = await repository_ratings.remove_rating(photo_id, current_user, db)
    return rating

