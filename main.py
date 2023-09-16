from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.testing import db
from fastapi.responses import JSONResponse
from database import engine, Base, get_db, Session
from routers import contact
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import HashPassword, create_user, authenticate_user, get_user_by_email,  \
    create_access_token, SECRET_KEY, ALGORITHM
from models import User, UserResponse, UserCreate, TokenResponse
from sqlalchemy.orm import Session
import jwt
from jose.exceptions import JWTError

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(contact.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


ACCESS_TOKEN_EXPIRE_MINUTES = 30


REFRESH_TOKEN_EXPIRE_MINUTES = 1440



@app.post("/register/", response_model=UserCreate)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
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
    return JSONResponse(content=user.dict(), status_code=status.HTTP_201_CREATED)


@app.post("/token/", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if user is None or not HashPassword().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")


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

@app.post("/refresh-token/", response_model=TokenResponse)
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:

        payload = decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
