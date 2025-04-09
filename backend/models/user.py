from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from sqlalchemy.types import DateTime
from pydantic import EmailStr
import uuid

class UserBase(SQLModel):
    first_name: str
    last_name: str | None = None
    email: EmailStr = Field(unique=True)

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

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc)
        },
        sa_type=DateTime(timezone=True)
    )
