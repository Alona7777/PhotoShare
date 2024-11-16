from typing import Sequence

from fastapi import HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, User
from src.conf import massages
from src.schemas.photo import SortDirection
from src.database.db import get_db


async def add_comment(
    comment_text: str, photo_id: int, user: User, db: AsyncSession = Depends(get_db)
) -> Comment:
    """
    The add_comment function adds a comment to the database.
    
    :param comment_text: str: Specify the text of the comment
    :param photo_id: int: Specify the photo that the comment is being added to
    :param user: User: Get the user object from the database
    :param db: AsyncSession: Pass in a database session, which is used to save the comment
    :return: The comment object that was created
    """
    new_comment = Comment(content=comment_text, user_id=user.id, photo_id=photo_id)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def get_comments_for_photo(
    photo_id: int, db: AsyncSession, sort_direction: SortDirection
) -> Sequence[Comment]:
    """
    The get_comments_for_photo function returns a list of comments for the photo with the given id.
    The sort_direction parameter determines whether to return them in ascending or descending order.
    
    :param photo_id: int: Filter the comments by photo_id
    :param db: AsyncSession: Pass in the database session
    :param sort_direction: SortDirection: Determine whether the comments should be sorted in ascending or descending order
    :return: A list of comments
    """
    select_comments = select(Comment).filter(Comment.photo_id == photo_id)
    if sort_direction == SortDirection.asc:
        query = select_comments.order_by(Comment.created_at)
    else:
        query = select_comments.order_by(Comment.created_at.desc())

    result = await db.execute(query)
    comments = result.scalars().all()
    return comments


async def get_comment_by_id(
    comment_id, user: User, db: AsyncSession = Depends(get_db)
) -> Comment:
    """
    The get_comment_by_id function takes a comment_id and user as arguments.
    It then filters the Comment table by id and user_id, executes the query,
    and returns a single result or None if no results are found.
    
    :param comment_id: Filter the comment by id
    :param user: User: Get the user id from the token
    :param db: AsyncSession: Get the database connection
    :return: A comment object
    """
    filter_comment = select(Comment).filter_by(id=comment_id, user_id=user.id)
    select_comment = await db.execute(filter_comment)
    get_comment = select_comment.scalar_one_or_none()
    if get_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=massages.NOT_COMMENT)
    return get_comment


async def update_comment(
    comment_id: int, comment_text: str, user: User, db: AsyncSession = Depends(get_db)
) -> Comment:
    """
    The update_comment function takes in a comment_id, comment_text, and user.
    It then filters the Comment table by the id of the comment and user id.
    If there is no matching row in the database it raises an HTTPException with status code 404 (NOT FOUND) 
    and detail message NOT_COMMENT. If there is a matching row it updates that rows content to be equal to 
    the new text passed into update_comment function and commits those changes to our database.
    
    :param comment_id: int: Identify the comment to be deleted
    :param comment_text: str: Update the comment content
    :param user: User: Get the user's id from the token
    :param db: AsyncSession: Get the database session
    :return: A comment object
    """
    filter_comment = select(Comment).filter_by(id=comment_id, user_id=user.id)
    select_comment = await db.execute(filter_comment)
    get_comment = select_comment.scalar_one_or_none()
    if get_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=massages.NOT_COMMENT)
    get_comment.content = comment_text
    await db.commit()
    await db.refresh(get_comment)
    return get_comment


async def delete_comment(
    comment_id: int, db: AsyncSession = Depends(get_db)
) -> Comment:
    """
    The delete_comment function deletes a comment from the database.
        Args:
            comment_id (int): The id of the comment to be deleted.
    
    :param comment_id: int: Get the comment id from the url
    :param db: AsyncSession: Get the database session
    :return: The deleted comment
    """
    filter_comment = select(Comment).filter_by(id=comment_id)
    select_comment = await db.execute(filter_comment)
    get_comment = select_comment.scalar_one_or_none()
    if get_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=massages.NOT_COMMENT)
    await db.delete(get_comment)
    await db.commit()
    return get_comment


