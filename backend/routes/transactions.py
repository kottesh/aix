from fastapi import APIRouter, Body, status, Depends, HTTPException
from fastapi.responses import JSONResponse 
from models.payment import PaymentType, Bank, Cash, Card
from sqlmodel import select 
from typing import Annotated
from models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    NLPTransactionCreate
)
from db import db_dependency
from models.user import User
from .auth import get_user
from uuid import UUID
from sqlalchemy.exc import NoResultFound
from datetime import datetime

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.post("/create-transaction", status_code=status.HTTP_200_OK)
def create_transaction(nlp_text: Annotated[str, Body()]) -> list[NLPTransactionCreate]:
    # TODO: use llm to extract structured transaction from text.
    pass

@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_transaction(
    *, transaction: TransactionCreate, user: User = Depends(get_user), db: db_dependency
) -> TransactionResponse:
    # TODO: need testing for this route as I have added the validation for payment methods.
    payment_id = transaction.payment_source_id
    payment_type = transaction.payment_source_type

    if payment_type == PaymentType.BANK:
        payment_id = db.exec(select(Bank).filter(Bank.id == transaction.payment_source_id)).one()
    elif payment_type == PaymentType.CARD:
        payment_id = db.exec(select(Card).filter(Card.id == transaction.payment_source_id)).one()
    elif payment_type == PaymentType.CASH:
        payment_id = db.exec(select(Cash).filter(Cash.id == transaction.payment_source_id)).one()

    if payment_id:
        transaction = Transaction(
            amount=transaction.amount,
            category=transaction.category,
            type=transaction.type,
            date=transaction.date,
            description=transaction.description,
            user_id=user.id,
            payment_source_id=payment_id,
            payment_source_type=payment_type
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="payment id not found.")

@router.delete("/remove")
def remove_transaction(transaction_id: Annotated[UUID, Body(embed=True)], db: db_dependency) -> dict[str, str]:
    try:
        transaction = db.exec(select(Transaction).filter(Transaction.id == transaction_id)).one() # searches for exactly only one record.
        db.delete(transaction)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "id": transaction.id,
                "message": "deleted successfully.",
            } 
        )
    except NoResultFound:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "transaction deletion failed.",
                "error": "transaction doesn't exists.",
            }
        )

@router.patch("/update", status_code=status.HTTP_200_OK)
def update_transaction(
    *, tid: UUID, update_data: TransactionUpdate, user: User = Depends(get_user), db: db_dependency
) -> TransactionResponse | JSONResponse:
    try:
        transaction: Transaction = db.exec(select(Transaction).filter(Transaction.id == tid)).one() # searches for exactly only one record.

        if update_data.amount:
            transaction.amount = update_data.amount
        if update_data.category:
            transaction.category = update_data.category
        if update_data.type:
            transaction.type = update_data.type
        if update_data.date:
            transaction.date = update_data.date
        if update_data.description:
            transaction.description = update_data.description
        
        if transaction.payment_source_type != update_data.payment_source_type:
            if update_data.payment_source_type == PaymentType.BANK:
                bank = db.exec(select(Bank).filter(Bank.id == update_data.payment_source_id)).first()

                if not bank:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Bank not found"
                    )

                transaction.payment_source_id = bank.id
                transaction.payment_source_type = PaymentType.BANK
            
            elif update_data.payment_source_id == PaymentType.CARD:
                card = db.exec(select(Card).filter(Card.id == update_data.payment_source_id)).first()

                if not card:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Card not found"
                    )

                transaction.payment_source_id = card.id
                transaction.payment_source_type = PaymentType.CARD

            elif update_data.payment_source_id == PaymentType.CASH:
                cash = db.exec(select(Cash).filter(Cash.id == update_data.payment_source_id)).first()

                if not cash:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cash not found"
                    )

                transaction.payment_source_id = cash.id
                transaction.payment_source_type = PaymentType.CASH
            
            db.add(transaction) 
            db.commit()

            return transaction

    except NoResultFound:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "transaction deletion failed.",
                "error": "transaction doesn't exists.",
            }
        )

@router.get("/")
def get_transactions(
    *,
    user: User = Depends(get_user),
    payment_type: PaymentType | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: db_dependency
) -> list[Transaction]:
    """
    Fetches transactions from the db and filters it out
    if no transactions found then just return `[]`
    """
    # TODO: we could improve the query more.
    # Instead of getting all the transactions and 
    # filtering it out in python.
    transactions = db.exec(select(Transaction).filter(Transaction.user_id == user.id)).all()

    if payment_type:
        transactions = [transaction for transaction in transactions if transaction.type == payment_type]

    if from_date:
        if to_date:
            transactions = [transaction for transaction in transactions if transaction.created_at >= from_date and transaction.created_at <= to_date]
        else:
            transactions = [transaction for transaction in transactions if transaction.created_at >= from_date]

    return transactions
