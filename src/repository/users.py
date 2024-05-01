from typing import Type

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> Type[User] | None:
    """
    The get_user_by_email function retrieves a user from the database based on the provided email.

    :param email: str: Specify the email of the user to retrieve
    :param db: Session: Pass in the database session object
    :return: A user object or none
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user using the provided UserModel instance and database session.

    :param body: UserModel: Pass the usermodel instance containing user information
    :param db: Session: Specify the database session to use for adding the new user
    :return: A user instance
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user in the database.

    :param user: User: Pass the user object to the function
    :param token: str | None: Pass the new refresh token to be assigned to the user
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function is used to confirm a user's email address.

    :param email: str: Specify the email address of the user to be confirmed
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> Type[User] | None:
    """
    The update_avatar function updates the avatar of a user in the database.

    :param email: Find the user in the database
    :param url: str: Specify the type of the parameter
    :param db: Session: Pass in the database session
    :return: The updated user object or none if the user is not found
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user