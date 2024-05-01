from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.config.config import settings
from src.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function reads the current user's information.

    :param current_user: User: Get the current user's information
    :return: The current user's information from the database
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function is used to update the avatar of a user.
        It takes in an UploadFile object, which contains the file containing the avatar image.
        It also takes in a User object, which represents the currently authenticated user.
        Finally it takes in a Session object, which represents our database session dependency.

    :param file: UploadFile: Upload the file to the server
    :param current_user: User: Get the currently authenticated user
    :param db: Session: Pass the database session to the function
    :return: The updated user object with the new avatar
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f'Notes/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'Notes/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user