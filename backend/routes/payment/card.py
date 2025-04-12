from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from db import db_dependency
from models import (
    User,
    Card,
    CardCreate,
    CardUpdate,
    CardResponse,
    Transaction,
    TransactionType,
    PaymentType
)
from datetime import datetime, timezone
from uuid import UUID
from ..utils import get_user


router = APIRouter(
    prefix="/card",
    tags=["card"]
)

def get_card(card_id: UUID, user_id: UUID, db: Session) -> Card | None:
    card = db.exec(
        select(Card)
        .filter(Card.user_id == user_id)
        .filter(Card.id == card_id)
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid Card. ID: {card_id}"
        )
    
    return card

@router.post("/", status_code=status.HTTP_200_OK)
def create_card(
    *,
    card_create_data: CardCreate,
    user: User = Depends(get_user),
    db: db_dependency
) -> CardResponse:
    balance = card_create_data.limit - card_create_data.current_usage

    card = Card(
        **card_create_data.__dict__,
        user_id=user.id,
        balance=balance
    )    

    db.add(card)
    db.commit()
    db.refresh(card)

    return CardResponse(**card.__dict__)

@router.delete("/{card_id}", status_code=status.HTTP_200_OK)
def remove_card(
    *,
    card_id: UUID,
    user: User = Depends(get_user),
    db: db_dependency
) -> dict[str, str]:
    card = get_card(card_id, user.id, db) 
    
    db.delete(card)
    db.commit()

    return {
        "message": "Card deleted successfully."
    } 

@router.patch("/{card_id}")
def update_card(
    *,
    card_id: UUID,
    card_update_data: CardUpdate,
    user: User = Depends(get_user),
    db: db_dependency
) -> CardResponse:
    card = get_card(card_id, user.id, db)

    if card_update_data.name:
        card.name = card_update_data.name
    if card_update_data.limit is not None and card_update_data.limit != card.limit:
        card.limit = card_update_data.limit
    if card_update_data.current_usage is not None and card_update_data.current_usage != card.current_usage:
        amount = abs(card.current_usage - card_update_data.current_usage)

        transaction_type = (
            TransactionType.IADJUST
            if card.current_usage > card_update_data.current_usage
            else TransactionType.DADJUST
        )

        adjustment_transaction = Transaction(
            user_id=user.id,
            type=transaction_type,      
            category="Adjustment",
            payment_source_id=card.id,
            payment_source_type=PaymentType.CARD,
            amount=amount,
            date=datetime.now(timezone.utc),
            description=f"Card usage adjusted from {card.current_usage} to {card_update_data.current_usage}"
        )

        if transaction_type == TransactionType.IADJUST:
            card.balance -= amount 
        else:
            card.balance += amount

        card.current_usage = card_update_data.current_usage

        db.add(adjustment_transaction)
    if card_update_data.currency:
        card.currency = card_update_data.currency
    if card_update_data.issuing_bank_name:
        card.issuing_bank_name = card_update_data.issuing_bank_name
    if card_update_data.network:
        card.network = card_update_data.network
    
    db.commit()
    db.refresh(card)

    return CardResponse(**card.__dict__)

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_cards(
    *,
    user: User = Depends(get_user),
    db: db_dependency
) -> list[CardResponse]:
    results = db.exec(
        select(Card)
        .filter(Card.user_id == user.id)
    ).all()

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nocards found."
        )

    cards = [CardResponse(**result.__dict__) for result in results] 

    return cards
    
@router.get("/{card_id}")
def get_card_by_id(
    *,
    card_id: UUID,
    user: User = Depends(get_user),
    db: db_dependency
) -> CardResponse:

    card = get_card(card_id, user.id, db)
    return card
