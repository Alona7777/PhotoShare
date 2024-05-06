from typing import List, Optional, Type, Sequence

from fastapi import HTTPException, Form, Depends
from sqlalchemy import select
# from sqlalchemy.orm import Session
from src.entity.models import Tag
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.tag import TagModel

from src.database.db import get_db


async def get_tags(skip: int, limit: int, db: AsyncSession) -> Sequence[Tag]:
    result = await db.execute(
        select(Tag)
        .offset(skip)
        .limit(limit)
    )
    tags = result.scalars().all()
    return tags


async def get_tag(tag_id: int, db: AsyncSession) -> Optional[Tag]:
    statement = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(statement)
    tag = result.scalars().first()
    return tag


async def create_tag(name_tag: str, db: AsyncSession = Depends(get_db)) -> Tag:
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
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()
    if tag:
        tag.name = body.name
        await db.commit()
        await db.refresh(tag)
    return tag


async def remove_tag(tag_id: int, db: AsyncSession) -> Optional[Tag]:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()

    if tag:
        await db.delete(tag)
        await db.commit()
        return tag
    return None
