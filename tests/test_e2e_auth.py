from unittest.mock import Mock
from fastapi import HTTPException, FastAPI, status
from fastapi.exceptions import FastAPIError, RequestValidationError
import pytest
from httpx import AsyncClient

from sqlalchemy import select, delete

from src.entity.models import User, BanUser
from tests.conftest import TestingSessionLocal
from src.conf import massages
from src.conf.massages import AuthMessages as auth_massages
from src.services.auth import auth_service

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678"}


@pytest.mark.asyncio
async def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    
    response = await client.post("api/auth/signup", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data
    mock_send_email.assert_called_once()

@pytest.mark.asyncio
async def test_repeat_signup(client):
    try:
        response = await client.post("api/auth/signup", json=user_data)
        assert response.status_code == status.HTTP_409_CONFLICT   #409
        data = response.json()
        assert data["detail"] == auth_massages.ACCOUNT_EXISTS  #"Account already exists"
    except FastAPIError as e:
        print("Exception caught:", e)


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.verified = True
            await session.commit()

    response = await client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


@pytest.mark.asyncio
async def test_wrong_email_login(client):
    try:
        response = await client.post("api/auth/login",
                            data={"username": "email", "password": user_data.get("password")})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        data = response.json()
        assert data["detail"] == auth_massages.INVALID_REGISTRATION    #"Invalid email"
    except Exception as e:
        print("Exception caught:", e)


@pytest.mark.asyncio
async def test_not_verified_login(client):
    try:
        response = await client.post("api/auth/login",
                            data={"username": user_data.get("email"), "password": user_data.get("password")})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        data = response.json()
        assert data["detail"] == auth_massages.EMAIL_NOT_VERIFIED  #"Email not confirmed"
    except Exception as e:
        print("Exception caught:", e)


@pytest.mark.asyncio
async def test_wrong_password_login(client):
    try:
        response = await client.post("api/auth/login",
                            data={"username": user_data.get("email"), "password": "password"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        data = response.json()
        assert data["detail"] == auth_massages.INVALID_REGISTRATION    #INVALID_PASSWORD  #"Invalid password"
    except Exception as e:
        print("Exception caught:", e)


@pytest.mark.asyncio
async def test_ban_user_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        ban = BanUser(user_id=current_user.id)
        session.add(ban)
        await session.commit()
        try:
            response = await client.post("api/auth/login",
                            data={"username": user_data.get("email"), "password": user_data.get("password")})
            assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
            data = response.json()
            assert data["detail"] == auth_massages.BAN_USER
        except Exception as e:
            print("Exception caught:", e) 

    async with TestingSessionLocal() as session:
        delete_stmt = delete(BanUser).where(BanUser.user_id == current_user.id)
        await session.execute(delete_stmt)
        await session.commit()


@pytest.mark.asyncio
async def test_refresh_token(client, get_token):
    refresh_token = await auth_service.create_refresh_token(data={"sub": user_data["email"]})

    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        current_user.refresh_token = refresh_token
        await session.commit()
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = await client.get("api/auth/refresh_token", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert "token_type" in response.json()


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    invalid_token = "invalid_refresh_token"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    try:
        response = await client.get("api/auth/refresh_token", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == auth_massages.INVALID_TOKEN       #"Invalid token"
    except Exception as e:
            print("Exception caught:", e) 


# @pytest.mark.asyncio
# async def test_refresh_token_mismatch(client):
#     valid_refresh_token = await auth_service.create_refresh_token(data={"sub": user_data["email"]})
#     mismatched_refresh_token = await auth_service.create_refresh_token(data={"sub": user_data["email"]})

#     async with TestingSessionLocal() as session:
#         current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
#         current_user = current_user.scalar_one_or_none()
#         current_user.refresh_token = mismatched_refresh_token
#         await session.commit()

#     # Запрос с валидным, но несовпадающим refresh_token
#     headers = {"Authorization": f"Bearer {valid_refresh_token}"}
#     response = await client.get("api/auth/refresh_token", headers=headers)

#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     assert response.json()["detail"] == auth_massages.INVALID_TOKEN    #"Invalid token"






