from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from uuid import UUID 
from datetime import datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: UUID
    email: str

class Token(SQLModel, table=True):
    __tablename__ = "token_blacklist"
    id: int = Field(default=None, primary_key=True)
    token: str
    expries_at: datetime
