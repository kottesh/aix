from fastapi import APIRouter, Depends, status, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select
from models.user import UserCreate, UserLogin, User, Token 
from typing import Annotated
from db import db_dependency 
from dotenv import load_dotenv
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import uuid

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = os.getenv("SECRET_KEY", "we love you tony stark infinite times")
ALGORITHM = "HS256"
TIMEDELTAHOURS = 2

oauth2_scheme =  OAuth2PasswordBearer(tokenUrl="auth/login")
bcrypt_context = CryptContext(schemes=["bcrypt"])

def get_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload["user_id"]
        user_email = payload["sub"]

        if user_id is None or  user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
        
        return {
            "user_id": user_id,
            "user_email": user_email
        }
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

def generate_jwt_token(user_id: uuid.UUID, user_email: str, time_delta: timedelta) -> str:
    payload = {
        "sub": user_email,
        "user_id": str(user_id),
        "exp": datetime.now() + time_delta
    }

    token = encode(payload=payload, algorithm=ALGORITHM, key=SECRET_KEY)

    return token


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_data: UserCreate) -> User:
    try:
        email = db.exec(select(User).where(User.email == user_data.email)).first()

        if email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")

        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=bcrypt_context.hash(user_data.password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user.")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(db: db_dependency, user_form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    try:
        """
        I am using the `username` instead of email,
        Becuase OAuth2PasswordRequestForm have username and password fieldsalone. 
        I'm considering username as email.
        """
        user = db.exec(select(User).where(User.email == user_form_data.username)).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found. Try to register")

        if not bcrypt_context.verify(user_form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect.")

        access_token = generate_jwt_token(user.id, user.email, timedelta(minutes=30))
        refresh_token = generate_jwt_token(user.id, user.email, timedelta(days=30))

        token = Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

        return token
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to login user.")

@router.post("/refresh")
async def refresh_token():
    pass

@router.post("/logout")
async def logout_user():
    # TODO: invalidate token
    pass
