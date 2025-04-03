from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from .payment import PaymentType
from datetime import datetime
from enum import Enum
import uuid

class TransactionType(str, Enum):
    EXPENSE = "Expense"
    INCOME = "Income"

class TransactionBase(SQLModel):
    amount: float
    category: str
    type: TransactionType
    date: datetime = Field(default_factory=datetime.now)
    description: str | None = None

class TransactionCreate(TransactionBase):
    date: datetime | None = None

class Transaction(TransactionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")

    payment_source_id: uuid.UUID
    payment_source_type: PaymentType

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
