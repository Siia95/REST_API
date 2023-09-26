from datetime import datetime, timedelta
from fastapi_mail import FastMail
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.testing import db
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from sqlalchemy import create_engine
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiterDependency
import auth
from database import engine, Base, get_db, Session
from routers import contact
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import HashPassword, create_user,confirmed_email, create_email_token, get_user_by_email,  \
    create_access_token, SECRET_KEY, ALGORITHM
from models import User, UserResponse, UserCreate, TokenResponse, RequestEmail
from sqlalchemy.orm import Session, sessionmaker
import jwt
from jwt import ExpiredSignatureError
from jose.exceptions import JWTError
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
from pydantic import EmailStr, BaseModel
from typing import List
from routers.contact import create_contact

class EmailSchema(BaseModel):
    email: EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME="test_for_mail@meta.ua",
    MAIL_PASSWORD="Grottersha95",
    MAIL_FROM="test_for_mail@meta.ua",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Example email",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(contact.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


ACCESS_TOKEN_EXPIRE_MINUTES = 30


REFRESH_TOKEN_EXPIRE_MINUTES = 1440


limiter = FastAPILimiter(
    key_func=lambda _: "global",  # Глобальне обмеження
    rate_limit="10/minute",  # Обмеження: не більше 10 запитів на хвилину
)
limiter_dependency = RateLimiterDependency(limiter)

app.include_router(create_contact.router)

origins = [
    "http://localhost:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://postgres:restapi@localhost/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.post("/update-avatar/")
async def update_avatar(user_id: int, avatar_url: str):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        user.avatar_url = avatar_url
        db.commit()
        db.close()
        return {"message": "Avatar updated successfully"}

    db.close()
    return {"message": "User not found"}



@app.post("/register/", response_model=UserCreate)
async def register_user(user: UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks(),
    request: Request = None):
    # Перевірка, чи користувач із таким email вже існує
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already registered")

    # Хешування пароля та створення запису користувача у базі даних
    hashed_password = HashPassword().hash_password(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return JSONResponse(content=user.dict(), status_code=status.HTTP_201_CREATED)

@app.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await get_user_by_email(body.email, db)

    if not user:
        return {"message": "User not found"}

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@app.post("/token/", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if user is None or not HashPassword().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")


    access_token_payload = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }


    access_token = jwt.encode(
        access_token_payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


    refresh_token_payload = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    }


    refresh_token = jwt.encode(
        refresh_token_payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


    token_response = TokenResponse(access_token=access_token, token_type="bearer", refresh_token=refresh_token)
    return token_response


@app.get("/protected/")
async def protected_route(current_user: User = Depends(oauth2_scheme)):
    return {"message": "This is a protected route", "user": current_user}


async def get_email_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        return email
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid token for email verification")


@app.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await get_email_from_token(token)
    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await auth.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@app.post("/refresh-token/", response_model=TokenResponse)
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")


        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")


        access_token = create_access_token(data={"sub": user.email})


        token_response = TokenResponse(access_token=access_token, token_type="bearer")
        return token_response
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = create_email_token({"sub": email})

        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionError as err:
        print(err)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="127.0.0.1", port=8000)
