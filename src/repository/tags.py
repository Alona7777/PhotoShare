from typing import List, Optional, Type
from sqlalchemy.orm import Session
from src.entity.models import Tag


async def create_tag(name, db: Session) -> Tag:
    """
The create_tag function creates a new tag in the database.

:param name: Create a new tag object
:param db: Session: Pass the database session to the function
:return: The tag object that was created
:doc-author: Trelent
"""
    tag = Tag(name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def get_tags(db: Session) -> List[Type[Tag]]:
    """
The get_tags function returns a list of all tags in the database.

:param db: Session: Pass in the database session
:return: A list of tags
:doc-author: Trelent
"""
    return db.query(Tag).all()


async def get_tag(tag_id: int, db: Session) -> Optional[Tag]:
    """
The get_tag function takes a tag_id and db as parameters.
It returns the first Tag object in the database that matches the given tag_id.

:param tag_id: int: Specify the tag id
:param db: Session: Pass the database session to the function
:return: A tag object
:doc-author: Trelent
"""
    return db.query(Tag).filter_by(id=tag_id).first()


async def get_tag_by_name(name: str, db: Session) -> Optional[Tag]:
    """
The get_tag_by_name function returns a Tag object from the database, given its name.

:param name: str: Specify the name of the tag to be searched for
:param db: Session: Pass the database session to the function
:return: The first tag with the name specified in the function arguments
:doc-author: Trelent
"""
    return db.query(Tag).filter_by(name=name).first()
