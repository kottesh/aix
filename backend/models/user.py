from sqlmodel import SQLModel, Field
from sqlalchemy import DateTime, func, Column
from datetime import datetime
from pydantic import BaseModel
import uuid

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserBase(SQLModel):
    name: str
    email: str = Field(unique=True)

class UserCreate(UserBase):
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(exclude=True)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={
            "onupdate": datetime.now
        }
    )
