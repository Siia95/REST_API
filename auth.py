from passlib.context import CryptContext

from config import settings
from models import User
from database import SessionLocal, Session
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
import jwt
from jose.exceptions import JWTError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class HashPassword:
    def __init__(self, rounds: int = 10):
        """
                Helper class for hashing and verifying passwords using bcrypt.

                :param rounds: The number of rounds for bcrypt.
                """
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.rounds = rounds

    def hash_password(self, password: str):
        """
                Hash the given password.

                :param password: The password to be hashed.
                :return: The hashed password.
                """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str):
        """
                Verify the given plain password against the hashed password.

                :param plain_password: The plain password to be verified.
                :param hashed_password: The hashed password.
                :return: True if the passwords match, False otherwise.
                """
        return self.pwd_context.verify(plain_password, hashed_password)


def create_user(username: str, email: str, password: str):
    """
        Create a new user.

        :param username: The username of the user.
        :param email: The email address of the user.
        :param password: The password of the user.
        :return: The created user.
        """
    hashed_password = pwd_context.hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db = SessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def authenticate_user(email: str, password: str):
    """
        Authenticate a user.

        :param email: The email address of the user.
        :param password: The password of the user.
        :return: The authenticated user.
        """
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    if user and pwd_context.verify(password, user.hashed_password):
        return user

async def get_user_by_email(email: str, db: Session) -> User:
    """
        Get a user by email.

        :param email: The email address of the user.
        :param db: Database session.
        :return: The user with the specified email or None if not found.
        """
    user = db.query(User).filter_by(email=email).first()
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
        Create an access token.

        :param data: The data to be encoded in the token.
        :param expires_delta: The expiration time for the token.
        :return: The created access token.
        """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def confirmed_email(email: str, db: Session) -> None:
    """
        Confirm the user's email.

        :param email: The email address of the user.
        :param db: Database session.
        """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

def create_email_token(data: dict):
    """
        Create an email confirmation token.

        :param data: The data to be encoded in the token.
        :return: The created email confirmation token.
        """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token.decode('utf-8')
