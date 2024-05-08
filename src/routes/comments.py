from typing import Optional, List, Sequence

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.entity.models import Comment, User, Role
from src.repository import comments as repository_comments
from src.repository import photos as repositories_photos
from src.repository import admin as repositories_admin
from src.services.roles import RoleAccess
from src.schemas.photo import CommentResponse, SortDirection
from src.services.auth import auth_service


router = APIRouter(prefix="/comments", tags=["comments"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.post(
    "/{photo_id}",
    description="Add comment.",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=CommentResponse,
)
async def add_comment(
    photo_id: int,
    comment_text: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Optional[Comment]:
    """
    The add_comment function creates a new comment for the photo with the given id.
        The function takes in three parameters:
            - photo_id: an integer representing the id of a photo to which we want to add a comment.
            - comment_text: A string containing text that will be added as a new comment on this photo. 
                This is required and must not be empty or null, otherwise an error will be thrown by FastAPI.
    :param photo_id: int: Identify the photo to which the comment is added
    :param comment_text: str: Get the text of the comment
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user who is logged in
    :param : Get the photo_id from the request
    :return: None if the photo_id doesn't exist
    """
    photo = await repositories_admin.get_photo_by_id(photo_id=photo_id, db=db)    
    comment = await repository_comments.add_comment(
        comment_text, photo_id, current_user, db
    )
    return comment


@router.get(
    "/{comment_id}",
    description="Get comment by id",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=20)),
    ],
    response_model=CommentResponse,
)
async def get_comment_by_id(
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Comment:
    """
    The get_comment_by_id function returns a comment by its id.
    :param comment_id: int: Get the comment by its id
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :param : Get the comment by id
    :return: A comment object
    """
    db_comment = await repository_comments.get_comment_by_id(
        comment_id, current_user, db
    )
    return db_comment


@router.get(
    "/photo/{photo_id}",
    description="Get all comments on photo",
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
) -> Sequence[Comment]:
    """
    The get_comments_by_photo_id function returns a list of comments for the specified photo.
    The function accepts an optional sort_direction parameter, which defaults to descending order.
    :param photo_id: int: Specify the photo id for which we want to get comments
    :param sort_direction: SortDirection: Determine whether the comments should be sorted in ascending or descending order
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the user who is making the request
    :param : Get the photo_id from the url
    :return: A list of comment objects
    """
    photo = await repositories_photos.get_photo_by_id(photo_id, current_user, db)
    comments = await repository_comments.get_comments_for_photo(
        photo_id, db, sort_direction
    )
    return comments


@router.post(
    "/comment/{comment_id}",
    description="Update comment.",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: int,
    comment_text: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Optional[Comment]:
    """
    The update_comment function updates a comment in the database.
        Args:
            comment_id (int): The id of the comment to update.
            comment_text (str): The new text for the updated Comment object.
    :param comment_id: int: Identify the comment that is to be deleted
    :param comment_text: str: Get the new comment text from the request body
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user
    :param : Get the comment id
    :return: The updated comment
    """
    comment_update = await repository_comments.update_comment(
        comment_id, comment_text, current_user, db
    )
    return comment_update


@router.delete(
    "/{comment_id}",
    description="Delete comment.",
    dependencies=[
        Depends(access_to_route_all),
        Depends(RateLimiter(times=10, seconds=20)),
    ],
    response_model=CommentResponse,
)
async def delete_comment(
    comment_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
):
    """
    The delete_comment function deletes a comment from the database.
        Args:
            comment_id (int): The id of the comment to be deleted.
    :param comment_id: int: Get the id of the comment to be deleted
    :param db: AsyncSession: Pass the database session to the repository layer
    :param : Get the comment_id from the url
    :return: The comment that was deleted
    """
    del_comment = await repository_comments.delete_comment(comment_id, db)
    return del_comment
