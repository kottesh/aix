from sqlmodel import SQLModel, Field
from sqlalchemy import DateTime, func, Column
from datetime import datetime
import uuid

class UserBase(SQLModel):
    name: str
    email: str = Field(unique=True)

class UserCreate(UserBase):
    password: str

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
