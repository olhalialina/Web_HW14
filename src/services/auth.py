import pickle
import redis

from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.config import messages
from src.config.config import settings
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function is used to verify a plain text password against a hashed password.
        The function returns True if the plain text password matches the hashed one, and False otherwise.

        :param self: Represent the instance of the class
        :param plain_password: Verify the password that is entered by the user
        :param hashed_password: Compare the hashed password to the plain_password parameter
        :return: True or false depending on whether the password matches
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password string and returns the hashed version of that password.
        The hashing algorithm used is determined by the CryptContext object passed to FastAPI when creating an instance of
        the Security class.

        :param self: Represent the instance of the class
        :param password: str: Pass in the password that is to be hashed
        :return: A hashed password
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates an access token based on the provided data and expiration time.

        :param self: Refer to the instance of the class
        :param data: dict: Store the data that is to be encoded into the access token
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: An encoded access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token.

        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: An encoded refresh token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function decodes a refresh token and returns the email associated with it.

        :param self: Access the class variables
        :param refresh_token: str: Pass the refresh token to be decoded
        :return: The email associated with the refresh token
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_SCOPE)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=messages.NOT_VALIDATE)

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used to retrieve the current user.
        It uses the OAuth2PasswordBearer scheme to validate and decode JWT tokens.
        If credentials are invalid or if no user with such email exists, it raises an HTTPException.

        :param self: Refer to the class itself
        :param token: str: Get the token from the request header
        :param db: Session: Get the database session
        :return: The current user based on the provided token
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.NOT_VALIDATE,
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)
        user = self.r.get(user_hash)
        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(user_hash, pickle.dumps(user))
            self.r.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user


def create_email_token(self, data: dict):
    """
    The create_email_token function creates a JWT token using the provided data dictionary.
    The function takes in a self parameter, which is an instance of the class, and a data parameter,
    which is a dictionary containing the data to encode. The function then copies this data into another
    dictionary called to_encode and adds two additional keys: iat (issued at) and exp (expiration).
    The iat key contains the current time in UTC format while exp contains 7 days from now in UTC format.
    Finally, we use jwt's encode method to create our token with our secret key.

    :param self: Refer to the instance of the class
    :param data: dict: Pass in a dictionary containing the data to encode
    :return: A jwt token encoded with the provided data and secret key
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    token = jwt.encode(to_encode, self.SECRET_KEY,
                       algorithm=self.ALGORITHM)
    return token


async def get_email_from_token(self, token: str):
    """
    The get_email_from_token function takes a token string as input and attempts to decode it using the SECRET_KEY and ALGORITHM.
    If successful, it extracts the email from the decoded payload and returns it.
    If an exception of type JWTError is caught, it prints the error and raises an HTTPException with status code 422
    and detail &quot;Invalid token for email verification&quot;.

    :param self: Refer to the instance of the class
    :param token: str: Pass in the token string
    :return: The email string
    """
    try:
        payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        email = payload["sub"]
        return email
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=messages.INVALID_TOKEN)


auth_service = Auth()