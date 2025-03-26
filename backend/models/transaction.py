from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
from account import Account

class TransactiontType(str, Enum):
    EXPENSE = "Expense"
    INCOME = "Income"

class Transaction(SQLModel):
    id: int | None = Field(default=None, primary_key=True) 
    account_id: int = Field(foreign_key="account.id")
    type: TransactiontType
    amount: float = Field()

    created_at: datetime = Field(default=datetime.now)
    updated_at: datetime = Field(default=datetime.now)

    account: Account = Relationship(back_populates="transactions")

