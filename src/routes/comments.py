from typing import Optional, List, Type

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.security import HTTPBearer
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.conf import messages
from src.database.db import get_db
from src.entity.models import Comment, User
from src.repository import comments as repository_comments, photos as repository_photos
from src.schemas import photo
from src.schemas.comments import CommentResponse, SortDirection
from src.schemas.user import UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get('{/comment_id}', description="Get comment by id",
            dependencies=[
                Depends(RateLimiter(times=10, seconds=60)),
            ],
            response_model=CommentResponse,
            )
async def get_comment_by_id(
        comment_id: int = Path(ge=1),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> Type[Comment]:
    db_comment = await repository_comments.get_comment_by_id(comment_id, db)
    if db_comment is None:
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
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> List[Comment]:
    photo = await repository_photos.get_photo_by_id(photo_id, current_user)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    comments = await repository_comments.get_comments_by_photo(photo_id, sort_direction, db)
    return comments


@router.post('/{photo_id}', description='Add comment.',
             dependencies=[Depends(RateLimiter(times=10, seconds=60)),
                           ],
             response_model=CommentResponse,
             )
async def add_comment(
        photo_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> Optional[Comment]:
    photo = await repository_photos.get_photos(photo_id, db, current_user)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    comment = await repository_comments.add_comment(photo_id, db, current_user)
    return comment


@router.patch('/{comment_id}', description='Update comment.',
              dependencies=[
                  Depends(RateLimiter(times=10, seconds=60)),
              ],
              response_model=CommentResponse,
              )
async def update_comment(
        comment_id: int = Path(ge=1),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> Comment:
    comment = await repository_comments.update_comment(comment_id, current_user, db)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete('/{comment_id}', description='Delete comment.',
               dependencies=[
                   Depends(RateLimiter(times=10, seconds=60)),
               ],
               response_model=CommentResponse,
               )
async def delete_comment(
        comment_id: int = Path(ge=1),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> dict:
    messages = await repository_comments.delete_comment(comment_id, current_user, db)
    return messages
