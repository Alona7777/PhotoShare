from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import config


conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="Contact Systems",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to verify their email address.
        The function takes in three parameters:
            -email: EmailStr, the user's email address.
            -username: str, the username of the user who is registering for an account.  This will be used in a greeting message within the body of the email sent to them.
            -host: str, this is where we are hosting our application (i.e., localhost).  This will be used as part of a URL that we send in our verification link.

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Get the username of the user who is trying to register
    :param host: str: Pass the hostname of the server to the template
    :return: A coroutine object, which is not a value
    :doc-author: Naboka Artem
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Verify your email !",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_email_reset_password(email: EmailStr, username: str, host: str):
    """
    The send_email_reset_password function sends an email to the user with a link to reset their password.

    :param email: EmailStr: Specify the email address of the user
    :param username: str: Display the username in the email template
    :param host: str: Create the link to reset password
    :return: A token
    :doc-author: Naboka Artem
    """
    try:
        token_reset_password = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Reset password !",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_reset_password},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)


async def send_message_password(email: EmailStr, username: str, host: str):
    """
    The send_message_password function sends an email to the user with a link to reset their password.
        Args:
            email (str): The user's email address.
            username (str): The username of the user who is trying to reset their password.
            host (str): The hostname of the server where this function is being run from.

    :param email: EmailStr: Check if the email is valid
    :param username: str: Get the username of the user who wants to reset his password
    :param host: str: Get the host of the website
    :return: A coroutine object
    :doc-author: Naboka Artem
    """
    try:
        message = MessageSchema(
            subject="Reset the password successfully !",
            recipients=[email],
            template_body={"host": host, "username": username},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="message.html")
    except ConnectionErrors as err:
        print(err)


async def send_random_password(email: EmailStr, username: str, host: str, password: str):
    """
    The send_random_password function sends an email to the user with a new random password.
        Args:
            email (str): The user's email address.
            username (str): The username of the account that is being reset.
            host (str): The hostname of the server where this account exists, e.g., &quot;example-server&quot;.  This will be used in
                constructing a link to login at https://&lt;host&gt;/login/.

    :param email: EmailStr: Validate the email address
    :param username: str: Pass the username to the template
    :param host: str: Get the host name of the website
    :param password: str: Pass the new password to the function
    :return: A coroutine, which is an object that represents a function that returns a future
    :doc-author: Naboka Artem
    """
    try:
        message = MessageSchema(
            subject="New password successfully !",
            recipients=[email],
            template_body={"host": host, "username": username, "password": password},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_random_password.html")
    except ConnectionErrors as err:
        print(err)
