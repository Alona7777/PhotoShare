from typing import List, Optional, Type, Sequence

from sqlalchemy import select
# from sqlalchemy.orm import Session
from src.entity.models import Tag
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.tag import TagModel


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


async def create_tag(body: TagModel, db: AsyncSession) -> Tag:
    tag = Tag(name=body.name)
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