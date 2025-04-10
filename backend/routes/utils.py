from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select, Session
from models.user import User
from models.token import TokenData, Token
from typing import Annotated
from db import db_dependency 
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import uuid


load_dotenv()


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

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
    
def generate_jwt_token(user_id: uuid.UUID, user_email: str, time_delta: timedelta) -> str:
    payload = {
        "sub": user_email,
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc) + time_delta
    }

    token = encode(payload=payload, algorithm=ALGORITHM, key=SECRET_KEY)

    return token
