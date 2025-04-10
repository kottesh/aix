from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from ..utils import get_user
from models import User, Bank, BankCreate, BankUpdate, BankResponse
from db import db_dependency
from sqlmodel import select
from uuid import UUID


router = APIRouter(
    prefix="/banks",
    tags=["bank"]
)


@router.post("/")
def create_bank_account(
    *,
    bank_data: BankCreate,
    user: User = Depends(get_user),
    db: db_dependency
) -> BankResponse:

    bank_exists = db.exec(
        select(Bank)
        .filter(Bank.account_no == bank_data.account_no)
    ).first()

    if bank_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bank with Account No: {bank_data.account_no} already exists.",
        )

    bank = Bank(**bank_data.__dict__, user_id=user.id)        

    db.add(bank)
    db.commit()
    db.refresh(bank)

    return BankResponse(**bank.__dict__)

@router.patch("/{bank_id}")
def update_bank(
    *,
    bank_id: UUID,
    bank_update_data: BankUpdate,
    user: User = Depends(get_user),
    db: db_dependency
) -> BankResponse:

    bank = db.exec(
        select(Bank)
        .filter(Bank.id == bank_id)
        .filter(Bank.user_id == user.id)
    ).first()

    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank with ID:{bank_id} doesn't exists.",
        )
    
    if bank_update_data.account_no and bank_update_data.account_no != bank.account_no:
        account_exists = db.exec(
            select(Bank.id)
            .filter(Bank.account_no == bank_update_data.account_no)
        ).first()

        if account_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bank with Account Number:{bank_update_data.account_no} already exists.",
            )

        bank.account_no = bank_update_data.account_no 

    if bank_update_data.name:
        bank.name = bank_update_data.name
    
    if bank_update_data.currency:
        bank.currency = bank_update_data.currency
    
    db.commit()
    db.refresh(bank)

    return BankResponse(**bank.__dict__)

@router.delete("/{bank_id}")
def remove_bank(
    *,
    bank_id: UUID,
    user: User = Depends(get_user),
    db: db_dependency
) -> JSONResponse:
    bank = db.exec(
        select(Bank)
        .filter(Bank.id == bank_id)
    ).first()

    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank with ID:{bank_id} doesn't exists.",
        )

    db.delete(bank)
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Bank account deleted successfully."
        }
    )

@router.get("/")
def get_bank_accounts(
    *,
    user: User = Depends(get_user),
    db: db_dependency
) -> list[Bank]:

    banks = db.exec(
        select(Bank)
        .filter(Bank.user_id == user.id)
    ).all()
    return banks

@router.get("/{bank_id}")
def get_bank_by_ac(
    *,
    bank_id: UUID,
    user: User = Depends(get_user),
    db: db_dependency
) -> BankResponse:

    bank = db.exec(
        select(Bank)
        .filter(Bank.user_id == user.id)
        .filter(Bank.id == bank_id)
    ).first()

    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank with ID:{bank_id} doesn't exists.",
        )

    return bank 
