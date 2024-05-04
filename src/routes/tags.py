from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query

from src.database.db import get_db
from src.entity.models import Role
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.tag import TagModel, TagResponse
from src.repository import tags as repository_tags
from src.conf.messages import AuthMessages

from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/tags', tags=["tags"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=List[TagResponse], dependencies=[Depends(access_to_route_all)])
async def read_tags(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    tags = await repository_tags.get_tags(skip, limit, db)
    return tags


@router.get("/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_to_route_all)])
async def read_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagResponse, dependencies=[Depends(access_to_route_all)])
async def create_tag(name_tag: str = Query(..., min_length=3, max_length=25),
                     db: AsyncSession = Depends(get_db)):
    tag = await repository_tags.create_tag(name_tag, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AuthMessages.verification_error)
    return tag


@router.put("/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_to_route_all)])
async def update_tag(body: TagModel, tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or you don't have enough rules to update")
    return tag


@router.delete("/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_to_route_all)])
async def remove_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or you don't have enough rules to delete")
    return tag
