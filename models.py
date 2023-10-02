from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel, EmailStr
from datetime import timedelta



class Contact(Base):
    """
        Database model for contacts.
        """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    birth_date = Column(Date)
    extra_data = Column(String, nullable=True)

class User(Base):
    """
        Database model for users.
        """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    confirmed = Column(Boolean, default=False)
    verification_tokens = relationship("VerificationToken", back_populates="user")
    avatar_url = Column(String)

class UserCreate(BaseModel):
    """
        Pydantic model for creating a new user.
        """
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    """
        Pydantic model for user response.
        """
    id: int
    username: str
    email: str

class TokenResponse(BaseModel):
    """
        Pydantic model for token response.
        """
    access_token: str
    token_type: str

class VerificationToken(Base):
    """
        Database model for verification tokens.
        """
    __tablename__ = "verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, default=func.now() + timedelta(minutes=30))

    user = relationship("User", back_populates="verification_tokens")

class RequestEmail(BaseModel):
    """
        Pydantic model for email requests.
        """
    email: EmailStr


