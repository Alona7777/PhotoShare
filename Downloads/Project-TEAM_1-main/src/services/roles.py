from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and takes arguments that are passed to it.
        In this case, we're passing a list of Role objects.

        :param self: Represent the instance of the class
        :param allowed_roles: list[Role]: Set the allowed_roles attribute
        :return: None
        :doc-author: Naboka Artem
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        The __call__ function is a decorator that takes in the request and user,
        and returns the response. The user is passed to this function by Depends(auth_service.get_current_user).
        The auth service will check if there's a valid token in the Authorization header of the request,
        and return an instance of User if it exists.

        :param self: Access the class attributes
        :param request: Request: Get the request object
        :param user: User: Pass the user object to the function
        :return: A function that can be used as a decorator
        :doc-author: Naboka Artem
        """
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN"
            )
