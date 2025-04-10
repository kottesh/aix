from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from models.user import UserCreate, User
from models.token import TokenResponse
from typing import Annotated
from db import db_dependency 
from jwt.exceptions import InvalidTokenError
from datetime import timedelta

from .utils import *

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, user_data: UserCreate) -> User:
    try:
        email = db.exec(select(User).filter(User.email == user_data.email)).first()

        if email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")

        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
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
def login_user(response: Response, db: db_dependency, user_form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
    try:
        """
        I am using the `username` instead of email,
        Becuase OAuth2PasswordRequestForm have username and password fieldsalone. 
        I'm considering username as email.
        """
        user = db.exec(select(User).filter(User.email == user_form_data.username)).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found. Try to register")

        if not bcrypt_context.verify(user_form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect.")

        access_token = generate_jwt_token(user.id, user.email, timedelta(minutes=30))
        refresh_token = generate_jwt_token(user.id, user.email, timedelta(days=30))

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=30 * 24 * 60 * 60, # after 30 days expire
            httponly=True,
            secure=True,
        )

        token = TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )

        return token
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to login user.")

@router.post("/refresh", status_code=status.HTTP_201_CREATED)
def refresh_token(request: Request, db: db_dependency) -> TokenResponse:
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh_token not found.")
    
    user_data = validate_token(refresh_token, db)

    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token.")
    
    new_access_token = generate_jwt_token(user_data.user_id, user_data.email, timedelta(minutes=30))

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer"
    )

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(response: Response, access_token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency) -> dict[str, str]:
    try:
        blacklist_token(access_token, db)
        response.delete_cookie("refresh_token")

        return {"message": "logged out successfully."}

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token.")
