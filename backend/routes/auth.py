from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select, Session
from models.user import UserCreate, User
from models.token import TokenData, Token, TokenResponse
from typing import Annotated
from db import db_dependency 
from dotenv import load_dotenv
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
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

def validate_token(token: str, db: Session) -> TokenData | None:
    try:
        blacklist_token = db.exec(select(Token).filter(Token.token == token)).first()

        if blacklist_token:
            return None
        
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub") or not payload.get("user_id"):
            return None

        return TokenData(
            email=payload.get("sub"),
            user_id=payload.get("user_id")
        )

    except ExpiredSignatureError:
        return None

    except InvalidTokenError:
        return None

def blacklist_token(token: str, db: Session):
    token_exists = db.exec(select(Token).filter(Token.token == token)).first()

    if token_exists:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expries_at = datetime.fromtimestamp(payload.get("exp"))
    expire_token = Token(
        token=token,
        expries_at=expries_at
    )
    db.add(expire_token)
    db.commit()
    db.refresh(expire_token)

def get_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency) -> User:
    token_data = validate_token(token, db)

    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    
    user: User = db.exec(select(User).filter(User.id == token_data.user_id)).first()

    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

def generate_jwt_token(user_id: uuid.UUID, user_email: str, time_delta: timedelta) -> str:
    payload = {
        "sub": user_email,
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc) + time_delta
    }

    token = encode(payload=payload, algorithm=ALGORITHM, key=SECRET_KEY)

    return token


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
