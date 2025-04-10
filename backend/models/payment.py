from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import DateTime
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

class PaymentType(str, Enum):
    BANK = "Bank"
    CARD = "Card"
    CASH = "Cash"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    JPY = "JPY"

class BankBase(SQLModel):
    name: str
    account_no: str = Field(max_length=64)
    amount: float = 0
    currency: Currency = Currency.INR

class BankCreate(BankBase):
    pass

class BankResponse(BankBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime 

class BankUpdate(BaseModel):
    name: str | None = None
    account_no: str | None = None
    currency: Currency | None = None

class Bank(BankBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")

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


class CashBase(SQLModel):
    amount: float = 0.0
    currency: Currency = Currency.INR

class CashCreate(CashBase):
    pass

class CashResponse(CashBase):
    id: uuid.UUID
    created_at: datetime 
    updated_at: datetime

class CashUpdate(BaseModel):
    amount: float | None = None
    currency: Currency | None = None

class Cash(CashBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE", unique=True)

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


class CardBase(SQLModel):
    name: str
    limit: float
    current_usage: float = 0
    currency: Currency = Currency.INR
    issuing_bank_name: str

class CardCreate(CardBase):
    pass

class Card(CardBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")

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
