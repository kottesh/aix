from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from db import db_dependency
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session
from models import (
    User,
    Cash,
    CashResponse,
    CashCreate,
    CashUpdate,
    Transaction,
    TransactionType,
    PaymentType,
)
from uuid import UUID
from datetime import datetime, timezone
from ..utils import get_user


router = APIRouter(
    prefix="/cash",
    tags=["cash"]
)

def get_cash(cash_id: UUID, user_id: UUID, db: Session) -> Cash:
    cash = db.exec(
        select(Cash)
        .filter(Cash.id == cash_id) 
        .filter(Cash.user_id == user_id)
    ).first()

    if not cash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cash Entry not found."
        )
    
    return cash


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_cash(
    *,
    cash_create_data: CashCreate,
    user: User = Depends(get_user),
    db: db_dependency
) -> CashResponse:

    try:
        cash = Cash(
            user_id=user.id,
            **cash_create_data.__dict__
        )

        db.add(cash)
        db.commit()
        db.refresh(cash)

        return CashResponse(**cash.__dict__) 

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more that one cash entry."
        )
    except Exception:
        raise

@router.patch("/{cash_id}", status_code=status.HTTP_200_OK)
def update_cash(
    *,
    cash_id: UUID,
    user: User = Depends(get_user),
    update_cash: CashUpdate,
    db: db_dependency
) -> CashResponse:

    cash = get_cash(cash_id, user.id, db)

    if update_cash.currency:
        cash.currency = update_cash.currency 
    if update_cash.amount:
        amount = abs(update_cash.amount - cash.amount)

        transaction = Transaction(
            amount=amount,
            category="Adjustment",
            type=TransactionType.IADJUST.value if update_cash.amount > cash.amount else TransactionType.DADJUST.value,
            date=datetime.now(timezone.utc),
            description=f"Ajustment from {cash.amount} to {update_cash.amount}",
            user_id=user.id,
            payment_source_id=cash.id,
            payment_source_type=PaymentType.CASH
        )

        db.add(transaction)

        cash.amount = update_cash.amount

    db.commit()
    db.refresh(cash)

    return CashResponse.model_validate(cash)

@router.delete("/{cash_id}", status_code=status.HTTP_200_OK)
def remove_cash(
    *,
    cash_id: UUID,
    user: User = Depends(get_user),
    db: db_dependency
) -> JSONResponse:

    cash = get_cash(cash_id, user.id, db)

    db.delete(cash)
    db.commit()

    return JSONResponse(
        content={
            "message": "Cash deleted successfully."
        }
    )

@router.get("/", status_code=status.HTTP_200_OK)
def get_cash_details(
    *,
    user: User = Depends(get_user),
    db: db_dependency
) -> CashResponse:

    cash = db.exec(
        select(Cash)
        .filter(Cash.user_id == user.id)
    ).first()

    if not cash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cash Entry not found."
        )

    print(cash.__dict__)
    return CashResponse(**cash.__dict__)
