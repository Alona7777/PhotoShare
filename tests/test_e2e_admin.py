import pytest

from pydantic_core import ValidationError

from unittest.mock import Mock
from tests.conftest import TestingSessionLocal

from fastapi import HTTPException, FastAPI, status
from fastapi.exceptions import FastAPIError, RequestValidationError

from httpx import AsyncClient

from sqlalchemy import select, delete

from src.entity.models import User, BanUser, Role
from src.schemas.user import RequestEmail
from src.conf import massages
from src.conf.massages import AuthMessages as auth_massages
from src.services.auth import auth_service
from src.entity.models import User, Photo 
from src.repository import users as repositories_users
from src.repository import photos as repositories_photos



@pytest.mark.asyncio
async def test_get_photos_as_admin(client, get_token, admin_user, new_user_with_photos):
    headers = {"Authorization": f"Bearer {get_token}"}

    new_user = new_user_with_photos

    assert admin_user is not None
    assert admin_user.role == Role.admin 

    # Verify that the new user exists and has photos
    async with TestingSessionLocal() as db:
        user_from_db = await repositories_users.get_user_by_email(new_user.email, db)
        assert user_from_db is not None
        assert user_from_db.id == new_user.id

        photos_from_db = await repositories_photos.get_photos(user=user_from_db, db=db, skip=2, limit=2)
        assert len(photos_from_db) == 2

    response = await client.get(f"/api/admin/all/{new_user.id}", headers=headers)
    assert response.status_code == 200
    photos = response.json()
    assert len(photos) == 5
    for photo in photos:
        assert "id" in photo
        assert "title" in photo
        assert "description" in photo
        assert "file_path" in photo

    # Test getting photos with pagination
    response = await client.get(f"/api/admin/all/{new_user.id}?skip=2&limit=2", headers=headers)
    assert response.status_code == 200
    photos = response.json()
    assert len(photos) == 2
    for photo in photos:
        assert "id" in photo
        assert "title" in photo
        assert "description" in photo
        assert "file_path" in photo


@pytest.mark.asyncio
async def test_get_photos_as_not_admin(client, new_user_with_photos):
    token = "some_token"
    headers = {"Authorization": f"Bearer {token}"}

    new_user = new_user_with_photos

    try:
        response = await client.get(f"/api/admin/all/{new_user.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    except FastAPIError as e:
        print("Exception caught:", e)
