from fastapi import APIRouter
from .auth import router as auth_router
from .transactions import router as transactions_router
from .user import router as users_router
from .payment import router as payment_router

router = APIRouter(
    prefix="/api/v1"
)

router.include_router(auth_router)
router.include_router(transactions_router)
router.include_router(users_router)
router.include_router(payment_router)
