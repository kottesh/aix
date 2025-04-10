from fastapi import APIRouter
from .bank import router as bank_router
from .cash import router as cash_router
from .card import router as card_router


router = APIRouter(
    prefix="/payment",
)

router.include_router(bank_router)
router.include_router(cash_router)
router.include_router(card_router)
