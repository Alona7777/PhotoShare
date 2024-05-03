from typing import Optional, List, Type, Sequence

from fastapi import HTTPException, status, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, User, Photo
from src.conf import messages
from src.schemas.photo import CommentModel, SortDirection
from src.database.db import get_db


async def add_comment(comment_text: str,
                      photo_id: int,
                      user: User,
                      db: AsyncSession = Depends(get_db)) -> Comment :
    new_comment = Comment(content=comment_text, user_id=user.id, photo_id=photo_id)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def get_comments_for_photo(photo_id: int,
                                 db: AsyncSession,
                                 sort_direction: SortDirection) -> Sequence[Comment] :
    select_comments = select(Comment).filter(Comment.photo_id == photo_id)
    if sort_direction == SortDirection.asc:
        query = select_comments.order_by(Comment.created_at)
    else:
        query = select_comments.order_by(Comment.created_at.desc())

    result = await db.execute(query)
    comments = result.scalars().all()

    return comments


async def get_comment_by_id(comment_id,
                            user: User,
                            db: AsyncSession = Depends(get_db)) -> Comment :
    filter_comment = select(Comment).filter_by(id=comment_id, user_id=user.id)
    select_comment = await db.execute(filter_comment)
    get_comment = select_comment.scalar_one_or_none()

    return get_comment


async def update_comment(comment_id: int,
                         comment_text: str,
                         user: User,
                         db: AsyncSession = Depends(get_db)) -> Comment:
    filter_comment = select(Comment).filter_by(id=comment_id, user_id=user.id)
    select_comment = await db.execute(filter_comment)
    get_comment = select_comment.scalar_one_or_none()
    if get_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    get_comment.content = comment_text
    await db.commit()
    await db.refresh(get_comment)
    return get_comment


async def delete_comment(comment_id: int,
                         db: AsyncSession = Depends(get_db)) -> Comment:
    filter_comment = select(Comment).filter_by(id=comment_id)
    select_comment = await db.execute(filter_comment)
    get_comment = select_comment.scalar_one_or_none()
    if get_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    await db.delete(get_comment)
    await db.commit()
    return get_comment


async def get_photo_by_id(
        photo_id: int, db: AsyncSession = Depends(get_db)
) -> Photo :
    """
    Get a photo by its id.

    :param user:
    :param photo_id: int: The id of the photo to get
    :param db: AsyncSession: The database session
    :return: Photo: The photo object
    """
    photo_expression = select(Photo).filter_by(id=photo_id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo :
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo
