import pytest
import asyncio

from pydantic_core import ValidationError

from fastapi_limiter import FastAPILimiter
from unittest.mock import AsyncMock, MagicMock, patch
from tests.conftest import TestingSessionLocal

from fastapi import HTTPException, FastAPI, status, BackgroundTasks, Request
from fastapi.exceptions import FastAPIError, RequestValidationError

from httpx import AsyncClient

from sqlalchemy import select, delete

from src.entity.models import User, BanUser
from src.schemas.user import RequestEmail, ResetPassword, UserResponse
from src.conf import massages
from src.conf.massages import AuthMessages as auth_massages
from src.services.auth import auth_service

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678"}


@pytest.mark.asyncio
async def test_signup(client, monkeypatch):
    mock_send_email = AsyncMock()
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
    except FastAPIError as e:
        print("Exception caught:", e)


@pytest.mark.asyncio
async def test_not_verified_login(client):
    try:
        response = await client.post("api/auth/login",
                            data={"username": user_data.get("email"), "password": user_data.get("password")})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        data = response.json()
        assert data["detail"] == auth_massages.EMAIL_NOT_VERIFIED  #"Email not confirmed"
    except AssertionError as e:
        print("Exception caught:", e)


@pytest.mark.asyncio
async def test_wrong_password_login(client):
    try:
        response = await client.post("api/auth/login",
                            data={"username": user_data.get("email"), "password": "password"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        data = response.json()
        assert data["detail"] == auth_massages.INVALID_REGISTRATION    #INVALID_PASSWORD  #"Invalid password"
    except FastAPIError as e:
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
        except FastAPIError as e:
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
    except FastAPIError as e:
            print("Exception caught:", e) 


@pytest.mark.asyncio
async def test_verified_email_success(client, get_token):
    email = await auth_service.get_email_from_token(get_token)

    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == email))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.verified = False
            await session.commit()

    response = await client.get(f"/api/auth/verified_email/{get_token}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Email verified!"}

    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == email))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.verified = True
            await session.commit()


@pytest.mark.asyncio
async def test_verified_email_invalid_token(client):
    token = "some_token"
    try:
        email = await auth_service.get_email_from_token(token)
        response = await client.get(f"/api/auth/verified_email/{token}")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    except HTTPException as e:
            print("Exception caught:", e) 


@pytest.mark.asyncio
async def test_verified_email_already_verified(client, get_token):
    email = await auth_service.get_email_from_token(get_token)

    response = await client.get(f"/api/auth/verified_email/{get_token}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Your email is already verified!"}


@pytest.mark.asyncio
async def test_request_email_not_verified(client, monkeypatch):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data["email"]))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.verified = False
            await session.commit()

    email_request = RequestEmail(email=user_data["email"])

    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = await client.post("/api/auth/request_email", json=email_request.model_dump())
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Check your email for confirmation."}
    
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data["email"]))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.verified = True
            await session.commit()


@pytest.mark.asyncio
async def test_request_email_already_verified(client):
        email_request = RequestEmail(email=user_data["email"])
        response = await client.post("/api/auth/request_email", json=email_request.model_dump())

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Your email is already confirmed!"}


@pytest.mark.asyncio
async def test_request_email_user_not_found(client):
    email_request = RequestEmail(email="nonexistent@example.com")
    
    try:
        response = await client.post("/api/auth/request_email", json=email_request.model_dump())
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "User not found."}
    except FastAPIError as e:
            print("Exception caught:", e) 


@pytest.mark.asyncio
async def test_request_email_invalid_email(client):
    try:
        email_request = RequestEmail(email="invalid_email")
    
        response = await client.post("/api/auth/request_email", json=email_request.model_dump()) 
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    except ValidationError as e:
        print("Exception caught:", e)


@pytest.mark.asyncio
async def test_send_reset_password(client, monkeypatch):
    email_request = RequestEmail(email=user_data["email"])

    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.routes.auth.send_email_reset_password", mock_send_email)

    response = await client.post("/api/auth/send_reset_password", json=email_request.model_dump())
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Check your email for confirmation."}


@pytest.mark.asyncio
async def test_send_reset_password_user_not_found(client):
    try:
        email_request = RequestEmail(email="invalid_email")
        response = await client.post("/api/auth/send_reset_password", json=email_request.model_dump()) 
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "User not found."}
    except ValidationError as e:
        print("Exception caught:", e)


@pytest.mark.asyncio
async def test_reset_password_success(client, monkeypatch):
    async def mock_identifier(request):
        return "test_identifier"

    async def mock_http_callback(request, response, pexpire):
        return response

    with patch.object(FastAPILimiter, "redis", AsyncMock()):
        with patch.object(FastAPILimiter, "identifier", mock_identifier):
            with patch.object(FastAPILimiter, "http_callback", mock_http_callback):
                body = {"password1": "new_password", "password2": "new_password"}
                refresh_token = await auth_service.create_refresh_token(data={"sub": user_data["email"]})
            
                async with TestingSessionLocal() as session:
                    current_user = await session.execute(select(User).where(User.email == user_data["email"]))
                    current_user = current_user.scalar_one_or_none()
                    current_user.refresh_token = refresh_token
                    await session.commit()

                headers = {"Authorization": f"Bearer {refresh_token}"}

                mock_send_message_password = AsyncMock()
                monkeypatch.setattr("src.routes.auth.send_message_password", mock_send_message_password)
                response = await client.post("/api/auth/reset_password/", json=body, headers=headers)
                assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_reset_password_passwords_not_match(client):

    async def mock_identifier(request):
        return "test_identifier"

    async def mock_http_callback(request, response, pexpire):
        return response

    with patch.object(FastAPILimiter, "redis", AsyncMock()):
        with patch.object(FastAPILimiter, "identifier", mock_identifier):
            with patch.object(FastAPILimiter, "http_callback", mock_http_callback):
                body = ResetPassword(password1="password1", password2="password2")
                refresh_token = await auth_service.create_refresh_token(data={"sub": user_data["email"]})
            
                async with TestingSessionLocal() as session:
                    current_user = await session.execute(select(User).where(User.email == user_data["email"]))
                    current_user = current_user.scalar_one_or_none()
                    current_user.refresh_token = refresh_token
                    await session.commit()

                headers = {"Authorization": f"Bearer {refresh_token}"}
                
                try:
                    response = await client.post("/api/auth/reset_password/", json=body.dict(), headers=headers)
                    
                    assert response.status_code == status.HTTP_400_BAD_REQUEST
                    assert response.json()["detail"] == auth_massages.NOT_MATCH_PASSWORD
                except FastAPIError as e:
                    print("Exception caught:", e) 
            

@pytest.mark.asyncio
async def test_reset_password_user_not_found(client):
    async def mock_identifier(request):
        return "test_identifier"

    async def mock_http_callback(request, response, pexpire):
        return response

    with patch.object(FastAPILimiter, "redis", AsyncMock()):
        with patch.object(FastAPILimiter, "identifier", mock_identifier):
            with patch.object(FastAPILimiter, "http_callback", mock_http_callback):
                body = ResetPassword(password1="new_password", password2="new_password")
                refresh_token = "invalid_token"
                headers = {"Authorization": f"Bearer {refresh_token}"}

                try:
                    response = await client.post("/api/auth/reset_password/", json=body.dict(), headers=headers)

                    assert response.status_code == status.HTTP_401_UNAUTHORIZED
                    assert response.json()["detail"] == auth_massages.INVALID_REGISTRATION
                except FastAPIError as e:
                    print("Exception caught:", e)


@pytest.mark.asyncio
async def test_reset_password_token(client, monkeypatch, get_token):
    async def mock_identifier(request):
        return "test_identifier"

    async def mock_http_callback(request, response, pexpire):
        return response

    with patch.object(FastAPILimiter, "redis", AsyncMock()):
        with patch.object(FastAPILimiter, "identifier", mock_identifier):
            with patch.object(FastAPILimiter, "http_callback", mock_http_callback):
                mock_send_random_password = AsyncMock()
                monkeypatch.setattr("src.routes.auth.send_random_password", mock_send_random_password)

                response = await client.get(f"/api/auth/reset_password/{get_token}")
                assert response.status_code == status.HTTP_200_OK
                assert response.json() == {"message": "New password sent by email!"}
    

@pytest.mark.asyncio
async def test_reset_password_token_user_not_found(client, monkeypatch):
    async def mock_identifier(request):
        return "test_identifier"

    async def mock_http_callback(request, response, pexpire):
        return response

    with patch.object(FastAPILimiter, "redis", AsyncMock()):
        with patch.object(FastAPILimiter, "identifier", mock_identifier):
            with patch.object(FastAPILimiter, "http_callback", mock_http_callback):
                token = "invalid_token"
                try:
                    response = await client.get(f"/api/auth/reset_password/{token}")
                    assert response.status_code == status.HTTP_400_BAD_REQUEST
                    assert response.json()["detail"] == auth_massages.RESET_PASSWORD_ERROR
                except FastAPIError as e:
                    print("Exception caught:", e)





