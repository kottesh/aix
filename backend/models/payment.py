from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, func, DateTime
from datetime import datetime
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
    amount: float = 0
    currency: Currency = Currency.INR

class BankCreate(BankBase):
    pass

class Bank(BankBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={
            "onupdate": datetime.now
        }
    )


class CashBase(SQLModel):
    amount: float = 0.0
    currency: Currency = Currency.INR

class CashCreate(CashBase):
    pass

class Cash(CashBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={
            "onupdate": datetime.now
        }
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

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={
            "onupdate": datetime.now
        }
    )
