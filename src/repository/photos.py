from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_photo(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no user is found, None is returned.

    :param email: str: Pass in the email of the user we want to get from our database
    :param db: AsyncSession: Connect to the database
    :return: A user object if the email exists in the database
    :doc-author: Naboka Artem
    """
    filter_user = select(User).filter_by(email=email)
    user = await db.execute(filter_user)
    user = user.scalar_one_or_none()
    return user