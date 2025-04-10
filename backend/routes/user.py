from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import select
from models.user import User, UserData
from .utils import get_user, bcrypt_context
from db import db_dependency
from typing import Annotated 
from sqlalchemy.exc import NoResultFound

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me")
async def get_user_info(user: User = Depends(get_user)) -> UserData:
    return user 

@router.post("/update/password")
async def update_password(
    *, user: User = Depends(get_user), new_password: Annotated[str, Body()], db: db_dependency
) -> dict[str, str]:
    if bcrypt_context.verify(new_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Create New password that is unlike your old password.")

    user.hashed_password = bcrypt_context.hash(new_password) 

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "password updated successfully"}

@router.post("/update/email")
async def update_email(
    *, user: User = Depends(get_user), new_email: Annotated[str, Body()], db: db_dependency
) -> dict[str, str]:
    email_exists = db.exec(select(User).filter(User.email == new_email)).first()

    if email_exists:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="email already exists.")

    user.email = new_email

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "email updated successfully"}

@router.delete("/close-account")
def close_account(*, user: User = Depends(get_user), db: db_dependency) -> dict[str, str]:
    try:
        user = db.exec(select(User).filter(User.id == user.id)).one()

        db.delete(user)
        db.commit()

        return {
            "id": user.id,
            "message": "account deleted successfully.",
        }
    except NoResultFound:
        return {
            "message": "account deletion failed.",
            "error": "account doesn't exists.",
        }
