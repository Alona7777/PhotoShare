from typing import Optional, List, Type, Sequence

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.db import get_db
from src.entity.models import Comment, User, Role
from src.repository import comments as repository_comments
from src.repository import photos as repositories_photos
from src.services.roles import RoleAccess
from src.schemas import photo
from src.schemas.photo import PhotoSchema, CommentResponse, SortDirection
from src.schemas.user import UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/comments", tags=["comments"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.post('/{photo_id}', description='Add comment.',
             dependencies=[Depends(RateLimiter(times=10, seconds=20))],
             response_model=CommentResponse,
             )
async def add_comment(
        photo_id: int,
        comment_text: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> Optional[Comment] :
    photo = await repository_comments.get_photo_by_id(photo_id, db)
    if photo is None :
        raise HTTPException(status_code=404, detail="Photo not found")
    comment = await repository_comments.add_comment(comment_text, photo_id, current_user, db)
    return comment


@router.get('/{comment_id}', description="Get comment by id",
            dependencies=[
                Depends(RateLimiter(times=10, seconds=20)),
            ],
            response_model=CommentResponse,
            )
async def get_comment_by_id(
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> Comment :
    db_comment = await repository_comments.get_comment_by_id(comment_id, current_user, db)
    if db_comment is None :
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.get('/photo/{photo_id}', description='Get all comments on photo',
            dependencies=[
                Depends(RateLimiter(times=10, seconds=60)),
            ],
            response_model=List[CommentResponse],
            )
async def get_comments_by_photo_id(
        photo_id: int = Path(ge=1),
        sort_direction: SortDirection = SortDirection.desc,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> Sequence[Comment] :
    photo = await repositories_photos.get_photo_by_id(photo_id, current_user, db)
    if photo is None :
        raise HTTPException(status_code=404, detail="Photo not found")
    comments = await repository_comments.get_comments_for_photo(photo_id, db, sort_direction)
    return comments


@router.post('/comment/{comment_id}', description='Update comment.',
             dependencies=[Depends(RateLimiter(times=10, seconds=20))],
             response_model=CommentResponse,
             )
async def update_comment(
        comment_id: int,
        comment_text: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> Optional[Comment] :
    comment_update = await repository_comments.update_comment(comment_id, comment_text, current_user, db)
    return comment_update


@router.delete('/{comment_id}', description='Delete comment.',
               dependencies=[Depends(access_to_route_all), Depends(RateLimiter(times=10, seconds=20))],
               response_model=CommentResponse,
               )
async def delete_comment(
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
):
    del_comment = await repository_comments.delete_comment(comment_id, db)
    if del_comment is None :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND
        )
    return del_comment
