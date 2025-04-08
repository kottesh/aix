from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import BaseModel
import uuid

class UserBase(SQLModel):
    first_name: str
    last_name: str | None = None
    email: str = Field(unique=True)

class UserCreate(UserBase):
    password: str

class UserData(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

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
