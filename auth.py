from passlib.context import CryptContext
from models import User
from database import SessionLocal
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
import jwt
from jose.exceptions import JWTError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "qaz_12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class HashPassword:
    def __init__(self, rounds: int = 10):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.rounds = rounds

    def hash_password(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)


def create_user(username: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db = SessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def authenticate_user(email: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    if user and pwd_context.verify(password, user.hashed_password):
        return user

def get_user_by_email(email: str):
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    db.close()
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

