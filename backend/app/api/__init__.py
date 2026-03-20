from fastapi import APIRouter

from .feedback.router import router as feedback_router
from .finance.router import router as finance_router
from .monitoring.router import router as monitoring_router
from .subscription.router import router as subscription_router
from .tickers.router import router as tickers_router
from .users.router import router as users_router

router = APIRouter()
router.include_router(users_router)
router.include_router(finance_router)
router.include_router(monitoring_router)
router.include_router(feedback_router)
router.include_router(subscription_router)
router.include_router(tickers_router)
