from typing import Optional

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.roles import RoleAccess
from src.database.db import get_db
from src.entity.models import User, Role, Rating
from src.schemas.rating import RatingModel, PhotoRating, ViewPhotoRating, QuantityRating
from src.repository import rating as repository_ratings
from src.services.auth import auth_service

router = APIRouter(prefix="/ratings", tags=["ratings"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.post(
    "/photo/{photo_id}",
    description="Add photo rating!",
    response_model=ViewPhotoRating,
    status_code=status.HTTP_201_CREATED,
)
async def create_photo_rating(
    photo_id: int = Path(ge=1),
    select_rating: PhotoRating = PhotoRating.five_stars,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Optional[Rating]:
    """
    The create_photo_rating function creates a rating for a photo.
        The function takes in the following parameters:
            - photo_id: int = Path(ge=0)
                - This is the id of the photo that will be rated. It must be greater than or equal to 0.
    
    :param photo_id: int: Get the photo id from the path
    :param select_rating: PhotoRating: Determine the rating that the user wants to give
    :param db: AsyncSession: Pass the database connection to the function
    :param current_user: User: Get the user who is currently logged in
    :param : Get the photo id from the url and is used to find a specific photo
    :return: A rating object
    """
    add_rating = await repository_ratings.create_rating_for_photo(
        photo_id, select_rating, current_user, db
    )
    return add_rating


@router.get("/photo/{image_id}", response_model=QuantityRating)
async def get_common_rating(image_id: int, db: AsyncSession = Depends(get_db)):
    """
    The get_common_rating function returns the average rating of a photo.
        Args:
            image_id (int): The id of the photo to be rated.
    
    :param image_id: int: Get the image id from the url
    :param db: AsyncSession: Pass the database session to the function
    :return: The average rating of an image
    """
    average_rating = await repository_ratings.get_average_rating(image_id, db)
    return average_rating


@router.get("/photo/{photo_id}", response_model=RatingModel)
async def read_tag(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The read_tag function returns the rating of a photo.
    
    :param photo_id: int: Specify the photo id
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get a database session
    :param : Get the current user from the database
    :return: The rating of the current user for a photo
    """
    rating = await repository_ratings.get_rating(photo_id, current_user, db)
    return rating


@router.get("/{rating_id}", response_model=RatingModel)
async def read_tag(rating_id: int, db: AsyncSession = Depends(get_db)):
    """
    The read_tag function returns a rating object with the given id.
    
    :param rating_id: int: Specify the rating_id of the rating to be updated
    :param db: AsyncSession: Pass the database session to the function
    :return: A rating object with the id specified in the path
    """
    rating = await repository_ratings.get_rating_id(rating_id, db)
    return rating


@router.put(
    "/{photo_id}", description="Update photo rating!", response_model=ViewPhotoRating
)
async def update_rating(
    photo_id: int = Path(ge=1),
    select_rating: PhotoRating = PhotoRating.five_stars,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Optional[Rating]:
    """
    The update_rating function is used to update the rating of a photo.
        The function takes in three parameters:
            - photo_id: This is the id of the photo that will be rated.
            - select_rating: This is an enum value that represents how many stars you want to rate a given picture with.  It can be one, two, three, four or five stars.  If no value is provided it defaults to five stars (the highest possible rating).
            - db: A database session object which allows us to interact with our database and make changes as needed for this particular request/response cycle.
    
    :param photo_id: int: Identify the photo to be rated
    :param select_rating: PhotoRating: Specify the rating that will be given to a photo
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Get the user object
    :param : Specify the type of data that will be returned by the function
    :return: A rating object or none if the photo does not exist
    """
    rating = await repository_ratings.create_rating_for_photo(
        photo_id, select_rating, current_user, db
    )
    return rating


@router.delete(
    "/{photo_id}",
    description="Delete photo rating!",
    dependencies=[Depends(access_to_route_all)],
)
async def remove_rating(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The remove_rating function removes a rating from the database.
    
    :param photo_id: int: Specify the photo that will be rated
    :param db: AsyncSession: Pass the database connection to the function
    :param current_user: User: Get the user that is currently logged in
    :param : Get the photo id
    :return: The removed rating
    """
    rating = await repository_ratings.remove_rating(photo_id, current_user, db)
    return rating
