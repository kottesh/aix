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
from .utils import get_user
from uuid import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy import desc
from datetime import datetime, timezone

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.post("/create-transaction", status_code=status.HTTP_200_OK)
def create_transaction(nlp_text: Annotated[str, Body()], user: User = Depends(get_user)) -> list[NLPTransactionCreate]:
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
def remove_transaction(*, transaction_id: Annotated[UUID, Body(embed=True)], user: User = Depends(get_user), db: db_dependency) -> dict[str, str]:
    try:
        transaction = db.exec(select(Transaction).filter(Transaction.id == transaction_id)).filter(Transaction.user_id == user.id).one() # searches for exactly only one record.
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
): 
    try:
        transaction: Transaction = db.exec(select(Transaction).filter(Transaction.id == tid)).filter(Transaction.user_id == user.id).one() # searches for exactly only one record if it doesn't find it raises Exception

        if update_data.amount:
            transaction.amount = update_data.amount
        if update_data.category:
            transaction.category = update_data.category
        if update_data.type:
            transaction.type = update_data.type
        if update_data.date:
            if update_data.date > datetime.now(timezone.utc):
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="invalid transaction date."
                )
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
            db.refresh(transaction)

            return TransactionResponse(**transaction.__dict__)

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
    n: int = 10,
    db: db_dependency
) -> list[Transaction]:
    # TODO: test this route having error in date comparsion.
    # Handle offset value in the datetime while comparing.
    """
    Fetches transactions from the db and filters it out
    if no transactions found then just return `[]`

    - user -> User who is performing the transaction request
    - payment_type[Optional] -> One of the BANK or CARD or CASH
    - from_date[Optional]
    - to_date[Optional]
    - n -> number of transactions to fetch with all the applied filters (DEFAULT: 10)
    """

    if from_date and from_date > datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date filter")

    if to_date and to_date > datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date filter")

    if (from_date and to_date) and from_date > to_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date filter")

    query = select(Transaction).filter(Transaction.user_id == user.id)

    if payment_type:
        query = query.filter(Transaction.payment_source_type == payment_type)

    if from_date:
        query = query.filter(Transaction.date >= from_date)
    if to_date:
        query = query.filter(Transaction.date <= to_date)
    
    query = query.order_by(Transaction.created_at.desc()).limit(n)

    transactions = db.exec(query).all()

    return transactions
