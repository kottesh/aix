from sqlmodel import SQLModel, Field
from datetime import datetime


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str
    email: str
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = None

