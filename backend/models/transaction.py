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
    payment_source_id: uuid.UUID
    payment_source_type: PaymentType

class TransactionUpdate(TransactionBase):
    payment_source_id: uuid.UUID
    payment_source_type: PaymentType

class TransactionResponse(TransactionBase):
    id: uuid.UUID
    payment_source_id: uuid.UUID
    payment_source_type: PaymentType
    created_at: uuid.UUID
    updated_at: uuid.UUID

class NLPTransactionCreate(TransactionCreate):
    pass

class Transaction(TransactionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")

    payment_source_id: uuid.UUID
    payment_source_type: PaymentType

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={
            "onupdate": datetime.now
        }
    )
