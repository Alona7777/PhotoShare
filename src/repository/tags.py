from typing import Optional, Sequence

from fastapi import HTTPException, Depends, status
from sqlalchemy import select
from src.entity.models import Tag
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.tag import TagModel

from src.database.db import get_db
from src.conf import messages


async def get_tags(skip: int, limit: int, db: AsyncSession) -> Sequence[Tag]:
    """
    The get_tags function returns a list of tags.
    
    :param skip: int: Skip a number of rows in the database
    :param limit: int: Limit the number of tags returned
    :param db: AsyncSession: Pass a database session to the function
    :return: A list of tag objects
    """
    result = await db.execute(select(Tag).offset(skip).limit(limit))
    tags = result.scalars().all()
    return tags


async def get_tag(tag_id: int, db: AsyncSession) -> Optional[Tag]:
    """
    The get_tag function takes a tag_id and an AsyncSession object as arguments.
    It then creates a select statement that selects all the tags from the Tag table where
    the id of the tag is equal to the given tag_id. It then executes this statement on 
    the database and gets back a result object which it uses to get all scalars in that 
    result set, which should be only one since we are looking for one specific id. If there is no such id, it raises an HTTPException with status code 404 (Not Found) and detail message NOT_TAG.
    
    :param tag_id: int: Specify the id of the tag we want to get
    :param db: AsyncSession: Pass the database session to the function
    :return: The tag object
    """
    statement = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(statement)
    tag = result.scalars().first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_TAG
        )
    return tag


async def create_tag(name_tag: str, db: AsyncSession = Depends(get_db)) -> Tag:
    """
    The create_tag function creates a new tag in the database.
        It takes a name_tag parameter, which is the name of the tag to be created.
        The function returns an instance of TagModel.
    
    :param name_tag: str: Create a new tag in the database
    :param db: AsyncSession: Connect to the database
    :return: The created tag
    """
    find_tag = await db.execute(select(Tag).filter_by(name=name_tag))
    find_tag = find_tag.scalars().first()
    if find_tag is not None:
        raise HTTPException(status_code=404, detail="This tag is in the database")
    tag = Tag(name=name_tag)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def update_tag(tag_id: int, body: TagModel, db: AsyncSession) -> Optional[Tag]:
    """
    The update_tag function updates a tag in the database.
        Args:
            tag_id (int): The id of the tag to update.
            body (TagModel): The new data for the specified Tag object.
    
    :param tag_id: int: Get the tag to update
    :param body: TagModel: Get the name of the tag
    :param db: AsyncSession: Pass the database session to the function
    :return: The updated tag
    """
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.NOT_TAG_OR_RULES,
        )
    tag.name = body.name
    await db.commit()
    await db.refresh(tag)
    return tag


async def remove_tag(tag_id: int, db: AsyncSession) -> Optional[Tag]:
    """
    The remove_tag function removes a tag from the database.
        Args:
            tag_id (int): The id of the tag to be removed.
    
    :param tag_id: int: Specify the tag that will be removed
    :param db: AsyncSession: Pass the database session to the function
    :return: A tag object
    """
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.NOT_TAG_OR_RULES,
        )
    await db.delete(tag)
    await db.commit()
    return tag


async def get_or_create_tag(tag_name: str, db: AsyncSession) -> Tag:
    """
    The get_or_create_tag function takes a tag name and an async database session as arguments.
    It then creates a select statement to find the tag in the database, executes it, and returns
    the result. If there is no such tag in the database, it creates one with that name and adds 
    it to the session. It then commits this change to the db before refreshing its own copy of 
    the object from what's now stored in db.
    
    :param tag_name: str: Specify the name of the tag
    :param db: AsyncSession: Pass the database session to the function
    :return: A tag object
    """
    statement = select(Tag).filter(Tag.name==tag_name)
    result = await db.execute(statement)
    tag = result.scalar_one_or_none()
    if tag is None:
        tag = Tag(name=tag_name)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag
    return tag


async def get_tag_name(tag_id: int, db: AsyncSession) -> str:
    """
    The get_tag_name function takes a tag_id and returns the name of the tag.
        If no such tag exists, it raises an HTTPException with status code 404.
    
    :param tag_id: int: Specify the id of the tag that we want to get
    :param db: AsyncSession: Pass the database session to the function
    :return: The tag name for a given tag id
    """
    statement = select(Tag.name).where(Tag.id == tag_id)
    result = await db.execute(statement)
    tag = result.scalars().first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_TAG
        )
    return tag



