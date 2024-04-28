from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
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


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session from the dependency
    :return: The newly created user
    :doc-author: Naboka Artem
    """
    avatar = None
    try:
        gravatar = Gravatar(body.email)
        avatar = gravatar.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Get the user's id
    :param token: str | None: Specify that the token parameter can be either a string or none
    :param db: AsyncSession: Pass the database session to the function
    :return: The user
    :doc-author: Naboka Artem
    """
    user.refresh_token = token
    await db.commit()


async def verified_email(email: str, db: AsyncSession) -> None:
    """
    The verified_email function takes in an email and a database session,
    and sets the verified field of the user with that email to True.


    :param email: str: Specify the email of the user to be verified
    :param db: AsyncSession: Pass the database session into the function
    :return: None
    :doc-author: Naboka Artem
    """
    user = await get_user_by_email(email, db)
    user.verified = True
    await db.commit()


async def update_user_password(email: str, password: str, db: AsyncSession) -> None:
    """
    The update_user_password function updates the password of a user in the database.
        Args:
            email (str): The email address of the user to update.
            password (str): The new password for this user.

    :param email: str: Find the user in the database
    :param password: str: Update the user's password
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Naboka Artem
    """
    user = await get_user_by_email(email, db)
    user.password = password
    await db.commit()
    await db.refresh(user)
    return user


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.

    :param email: str: Specify the email of the user whose avatar url we want to update
    :param url: str | None: Specify that the url parameter can be either a string or none
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Naboka Artem
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
