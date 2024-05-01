from typing import Optional, List, Type

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.entity.models import Comment, User
from src.conf import messages
from src.schemas.photo import CommentModel, SortDirection


async def add_comment(body: CommentModel,
                      photo_id: int,
                      user: User, db: Session) -> Optional[Comment]:
    comment = Comment(comment=body.comment, user_id=user.id, photo_id=photo_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)


async def update_comment(comment_id: int,
                         body: CommentModel,
                         user: User,
                         db:Session) -> Optional[Comment]:
    comment: Optional[Comment] = db.query(Comment).filter_by(id=comment_id).first()
    if not comment or not body.comment:
        return None
    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
    comment.comment = body.comment
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def delete_comment(comment_id: int,
                         user: User,
                         db: Session) -> dict:
    comment: Optional[Comment] = db.query(Comment).filter_by(id=comment_id).first()
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    db.delete(comment)
    db.commit()
    return {'message': messages.comment_deleted}


async def get_comments(photo_id, db) -> List[Comment]:
    return db.query(Comment).filter_by(photo_id=photo_id).all()


async def get_comment_by_id(comment_id: int, db: Session) -> Type[Comment]:
    return db.query(Comment).filter_by(id=comment_id).first()


async def get_comments_by_photo(photo_id: int,
                                sort_direction: SortDirection,
                                db: Session) -> List[Type[Comment]]:
    query = db.query(Comment).filter_by(photo_id=photo_id)
    if sort_direction == SortDirection.desc:
        comments = query.order_by(desc(Comment.id)).all()
    else:
        comments = query.order_by(Comment.id).all()
    return comments
