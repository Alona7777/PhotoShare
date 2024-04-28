import string
import random

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repositories_users
from src.services.email import send_email, send_email_reset_password, send_message_password, send_random_password
from src.schemas.user import UserSchema, UserResponse, TokenSchema, RequestEmail, ResetPassword
from src.services.auth import auth_service

router = APIRouter(prefix = '/auth', tags = ['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model = UserResponse, status_code = status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)) :
    """
    The signup function creates a new user in the database.
        It takes in a UserSchema object, which is validated by pydantic.
        If the email already exists, it returns an HTTP 409 Conflict error.
        Otherwise, it hashes the password and adds a new user to the database.

    :param body: UserSchema: Validate the request body
    :param bt: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the server
    :param db: AsyncSession: Get the database session
    :return: The new user
    :doc-author: Naboka Artem
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user :
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Account already exists!")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model = TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) :
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, and returns an access token if successful.
        The access token can be used to make requests on behalf of that user.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Get the database connection
    :return: A dictionary with the following keys:
    :doc-author: Naboka Artem
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None :
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid registration information!")
    if not user.verified :
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Email not verified!")
    if not auth_service.verify_password(body.password, user.password) :
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Incorrect registration information!")

    # Generate JWT token
    access_token = await auth_service.create_access_token(data = {"sub" : user.email})
    refresh_token = await auth_service.create_refresh_token(data = {"sub" : user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token" : access_token, "refresh_token" : refresh_token, "token_type" : "bearer"}


@router.get('/refresh_token', response_model = TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)) :
    """
    The refresh_token function is used to refresh the access token.
        It takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the header
    :param db: AsyncSession: Get the database session
    :return: A dictionary with the access_token, refresh_token and token type
    :doc-author: Naboka Artem
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token :
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid refresh token!")

    access_token = await auth_service.create_access_token(data = {"sub" : email})
    refresh_token = await auth_service.create_refresh_token(data = {"sub" : email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token" : access_token, "refresh_token" : refresh_token, "token_type" : "bearer"}


@router.get('/verified_email/{token}')
async def verified_email(token: str, db: AsyncSession = Depends(get_db)) :
    """
    The verified_email function is used to verify a user's email address.
        It takes in the token that was sent to the user's email and uses it to get their email address.
        Then, it checks if there is a user with that email in the database. If not, then an error message will be returned.
        If there is a user with that email, then we check if they are already verified or not:
            -If they are already verified, then we return an appropriate message saying so;
            -Otherwise (if they aren't yet verified), we update their status as &quot;verified&quot; and return

    :param token: str: Get the email from the token
    :param db: AsyncSession: Connect to the database
    :return: A message that the email is already verified or a message that it has been verified
    :doc-author: Naboka Artem
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None :
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Verification error!")
    if user.verified :
        return {"message" : "Your email is already verified!"}
    await repositories_users.verified_email(email, db)
    return {"message" : "Email verified!"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)) :
    """
    The request_email function is used to send a confirmation email to the user.
        The function takes in an email address and sends a confirmation link to that address.
        If the user's account has already been verified, then they will be notified of this fact.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the server
    :param db: AsyncSession: Connect to the database
    :return: A message to the user
    :doc-author: Naboka Artem
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.verified :
        return {"message" : "Your email is already confirmed!"}
    if user :
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message" : "Check your email for confirmation."}


@router.post('/send_reset_password')
async def send_reset_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                              db: AsyncSession = Depends(get_db)) :
    """
    The send_reset_password function is used to send an email to the user with a link that will allow them
    to reset their password. The function takes in a RequestEmail object, which contains the email of the user
    who wants to reset their password. It then checks if there is a user with that email address and sends them
    an email containing instructions on how they can reset their password.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Run the send_email_reset_password function in a background task
    :param request: Request: Get the base url of the server
    :param db: AsyncSession: Get the database session
    :return: A message to the user
    :doc-author: Naboka Artem
    """
    user = await repositories_users.get_user_by_email(body.email, db)
    print(user)
    if user :
        background_tasks.add_task(send_email_reset_password, user.email, user.username, str(request.base_url))
    return {"message" : "Check your email for confirmation."}


@router.post('/reset_password/',
             response_model = UserResponse,
             dependencies = [Depends(RateLimiter(times = 1, seconds = 20))], )
async def reset_password(body: ResetPassword,
                         background_tasks: BackgroundTasks,
                         request: Request,
                         db: AsyncSession = Depends(get_db),
                         credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token), ) :
    """
    The reset_password function is used to reset a user's password.
        It takes in the following parameters:
            body (ResetPassword): The new password for the user.
            background_tasks (BackgroundTasks): A list of tasks that are run in the background. This is used to send an email to the user confirming their new password has been set successfully.
            request (Request): The HTTP request object, which contains information about what was sent by the client and how it was sent, such as headers and URL arguments/parameters.

    :param body: ResetPassword: Get the password from the user
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: AsyncSession: Get the database session
    :param credentials: HTTPAuthorizationCredentials: Get the refresh token
    :param : Send the email to the user
    :return: The user object
    :doc-author: Naboka Artem
    """
    if body.password1 is body.password2 :
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Password doesn't match")
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user :
        password = auth_service.get_password_hash(body.password1)
        new_user = await repositories_users.update_user_password(email, password, db)
        user = await repositories_users.get_user_by_email(user.email, db)
        background_tasks.add_task(send_message_password, user.email, user.username, str(request.base_url))
        return user
    else :
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid registration information!")


@router.get('/reset_password/{token}',
            dependencies = [Depends(RateLimiter(times = 1, seconds = 20))], )
async def reset_password(bt: BackgroundTasks, request: Request,
                         token: str, db: AsyncSession = Depends(get_db),
                         ) :
    """
    The reset_password function is used to reset a user's password.
        It takes in the token from the email sent to the user and returns a new random password.

    :param bt: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base_url of the application
    :param token: str: Get the user's email from the token
    :param db: AsyncSession: Get the database session
    :param : Send the email in background
    :return: A message that a new password has been sent by email
    :doc-author: Naboka Artem
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None :
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Reset password error!")
    characters = string.ascii_letters + string.digits + string.punctuation
    password1 = ''.join(random.choice(characters) for i in range(8))
    password = auth_service.get_password_hash(password1)
    print(password1)
    new_user = await repositories_users.update_user_password(email, password, db)
    # user = await repositories_users.get_user_by_email(user.email, db)
    bt.add_task(send_random_password, user.email, user.username, str(request.base_url), password1)
    return {"message" : "New password sent by email!"}
