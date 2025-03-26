from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from transaction import Transaction
from enum import Enum

class AccountType(str, Enum):
    CASH = "Cash"
    BANK = "Bank"
    CARD = "Card"

class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str | None = Field(default=None, max_length=64)
    type: AccountType
    balance: float = 0
    user_id: int = Field(foreign_key="user.id")
    bank_name: str | None = Field(default=None, max_length=64)

    created_at: datetime = Field(default=datetime.now)
    updated_at: datetime = Field(default=datetime.now)

    transactions: list[Transaction] = Relationship(back_populates="account")
