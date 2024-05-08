from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import Role
from src.schemas.tag import TagModel, TagResponse
from src.repository import tags as repository_tags
from src.conf.messages import AuthMessages
from src.services.roles import RoleAccess


router = APIRouter(prefix="/tags", tags=["tags"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get(
    "/", response_model=List[TagResponse], dependencies=[Depends(access_to_route_all)]
)
async def read_tags(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    The read_tags function returns a list of tags.
    
    :param skip: int: Skip the first n tags
    :param limit: int: Limit the number of tags returned
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of tags
    """
    tags = await repository_tags.get_tags(skip, limit, db)
    return tags


@router.get(
    "/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_to_route_all)]
)
async def read_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    """
    The read_tag function is used to read a tag from the database.
        It takes in an integer, which represents the id of the tag that you want to read.
        The function returns a TagResponse object, which contains all of the information about that particular tag.
    
    :param tag_id: int: Specify the tag id that we want to update
    :param db: AsyncSession: Pass the database session to the function
    :return: A tag object
    """
    tag = await repository_tags.get_tag(tag_id, db)
    return tag


@router.post(
    "/", response_model=TagResponse, dependencies=[Depends(access_to_route_all)]
)
async def create_tag(
    name_tag: str = Query(..., min_length=3, max_length=25),
    db: AsyncSession = Depends(get_db),
):
    """
    The create_tag function creates a new tag in the database.
        The function takes a name_tag parameter, which is required and must be between 3 and 25 characters long.
        It also takes an optional db parameter, which is used to access the database.
    
    :param name_tag: str: Get the name of the tag to be created
    :param min_length: Specify the minimum length of a string
    :param max_length: Limit the length of the name_tag parameter
    :param db: AsyncSession: Pass the database connection to the function
    :param : Get the tag id from the url
    :return: A dictionary with the tag created
    """
    tag = await repository_tags.create_tag(name_tag, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=AuthMessages.VERIFICATION_ERROR,
        )
    return tag


@router.put(
    "/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_to_route_all)]
)
async def update_tag(body: TagModel, tag_id: int, db: AsyncSession = Depends(get_db)):
    """
    The update_tag function updates a tag in the database.
        It takes a TagModel object as input, and returns an updated TagResponse object.
    
    :param body: TagModel: Get the data from the request body
    :param tag_id: int: Identify the tag to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :return: A tagmodel object
    """
    tag = await repository_tags.update_tag(tag_id, body, db)
    return tag


@router.delete(
    "/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_to_route_all)]
)
async def remove_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    """
    The remove_tag function removes a tag from the database.
        ---
        tags:
            - Tags
    
    :param tag_id: int: Specify the id of the tag to be deleted
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A tag object
    """
    tag = await repository_tags.remove_tag(tag_id, db)
    return tag

