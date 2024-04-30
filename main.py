import redis.asyncio as redis
import re
from ipaddress import ip_address
from typing import Callable
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import auth, users, photos
from src.conf.config import config

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# banned_ips = [
#     ip_address("127.0.0.1"),
# ]
#
#
# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(status_code = status.HTTP_403_FORBIDDEN, content = {"detail": "You are banned"})
#     response = await call_next(request)
#     return response

ALLOWED_IPS = [ip_address("127.0.0.1"),]


@app.middleware("http")
async def limit_access_by_ip(request: Request, call_next: Callable):
    """
    The limit_access_by_ip function is a middleware function that limits access to the API by IP address.
    It checks if the client's IP address is in ALLOWED_IPS, and if not, returns a 403 Forbidden response.

    :param request: Request: Access the request object
    :param call_next: Callable: Pass the next function in the chain
    :return: A jsonresponse object with a status code of 403 and a message
    :doc-author: Trelent
    """
    ip = ip_address(request.client.host)
    if ip not in ALLOWED_IPS:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    response = await call_next(request)
    return response


user_agent_ban_list = [r"Googlebot", r"Python-urllib", r"bot-Yandex"]


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    The user_agent_ban_middleware function is a middleware function that checks the user-agent header of an incoming request.
    If the user-agent matches any of the patterns in our ban list, then we return a 403 Forbidden response. Otherwise, we call
    the next middleware function and return its response.

    :param request: Request: Access the request object
    :param call_next: Callable: Pass the request to the next middleware in line
    :return: A jsonresponse object that contains a status code of 403 and a detail message
    :doc-author: Naboka Artem
    """
    print(request.headers.get("Authorization"))
    user_agent = request.headers.get("user-agent")
    print(user_agent)
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response


app.include_router(auth.router, prefix = "/api")
app.include_router(users.router, prefix = "/api")
app.include_router(photos.router, prefix = "/api")
# app.include_router(birthday.router, prefix = "/api")


@app.on_event("startup")
async def startup() :
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like database connections or caches.

    :return: A list of functions to run after startup
    :doc-author: Naboka Artem
    """
    r = await redis.Redis(
        host = config.REDIS_DOMAIN,
        port = config.REDIS_PORT,
        db = 0,
        password = config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def index() :
    """
    The index function responds to a request for /api/v2/contacts
        with the complete lists of contacts

    :return: A dictionary with the key &quot;message&quot; and value &quot;contacts application&quot;
    :doc-author: Naboka Artem
    """
    return {"message" : "Contacts Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)) :
    """
    The healthchecker function is used to check the health of the database.
    It does this by making a simple query to the database and checking if it returns any results.
    If no results are returned, then we know that there is an issue with our connection.

    :param db: AsyncSession: Inject the database session into the function
    :return: A dictionary with a message
    :doc-author: Naboka Artem
    """
    try :
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None :
            raise HTTPException(status_code = 500, detail = "Database is not configured correctly")
        return {"message" : "Welcome to FastAPI!"}
    except Exception as e :
        print(e)
        raise HTTPException(status_code = 500, detail = "Error connecting to the database")


if __name__ == "__main__" :
    uvicorn.run(
        "main:app", host = "127.0.0.1", port = 8080, reload = True
    )
