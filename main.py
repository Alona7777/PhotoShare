import os
import pathlib

import redis.asyncio as redis
import re
from ipaddress import ip_address
from typing import Callable, List
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, status, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import expression
from starlette.staticfiles import StaticFiles
from src.database.db import get_db
from src.entity.models import Photo
from src.routes import auth, users, photos, transformation, comments, rating, tags, admin

from src.conf.config import config
from src.utils.py_logger import get_logger

from fastapi.templating import Jinja2Templates

from fastapi.security import OAuth2PasswordBearer

from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

logger = get_logger(__name__)

load_dotenv()

SECRET_KEY_JWT = os.getenv('SECRET_KEY_JWT')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
The lifespan function is a callback that will be executed when the application
starts up and shuts down. It's useful for performing expensive initialization
tasks, such as connecting to a database or initializing caches.

:param app: FastAPI: Pass the fastapi object to the function
:return: A generator
:doc-author: Trelent
"""
    logger.info(f"lifespan running")
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)
    yield


app = FastAPI(lifespan=lifespan, title="PhotoShare", description="API to manage photos", version="1.0.0",
              swagger_ui_parameters={"operationsSorter": "method"})

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ALLOWED_IPS = [ip_address("127.0.0.1", 'localhost:8000'), ]
#
#
# @app.middleware("http")
# async def limit_access_by_ip(request: Request, call_next: Callable):
#
#     ip = ip_address(request.client.host)
#     if ip not in ALLOWED_IPS:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
#     response = await call_next(request)
#     return response
#
#
# user_agent_ban_list = [r"Googlebot", r"Python-urllib", r"bot-Yandex"]


# @app.middleware("http")
# async def user_agent_ban_middleware(request: Request, call_next: Callable):
#
#     print(request.headers.get("Authorization"))
#     user_agent = request.headers.get("user-agent")
#     print(user_agent)
#     for ban_pattern in user_agent_ban_list:
#         if re.search(ban_pattern, user_agent):
#             return JSONResponse(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 content={"detail": "You are banned"},
#             )
#     response = await call_next(request)
#     return response


templates = Jinja2Templates(directory='templates')
BASE_DIR = pathlib.Path(__file__).parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@app.get("/protected-resource")
async def protected_resource(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY_JWT, algorithms=["HS256"])
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": f"Access granted to {email}"}


@app.get('/', response_class=HTMLResponse, description='main page')
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, 'title': 'PhotoShare App'})


@app.get('/auth')
async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get('/signup')
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get('/upload')
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/api/photos/all", response_model=List[dict])
async def get_all_photos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(oauth2_scheme)
):

    expression = select(Photo).offset(skip).limit(limit)
    result = await db.execute(expression)
    photos = result.scalars().all()
    return [{"id": photo.id, "title": photo.title, "description": photo.description, "file_path": photo.file_path} for photo in photos]

app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(transformation.router, prefix="/api")
app.include_router(tags.router, prefix='/api')
app.include_router(rating.router, prefix='/api')


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        logger.error(f"[ERROR]: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="127.0.0.1", port=8000, reload=True
    )
