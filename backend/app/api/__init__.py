from fastapi import APIRouter

from .depots.router import router as depots_router
from .feedback.router import router as feedback_router
from .finance.router import router as finance_router
from .init.router import router as init_router
from .monitoring.router import router as monitoring_router
from .tickers.router import router as tickers_router
from .users.router import router as users_router

router = APIRouter()
router.include_router(init_router)
router.include_router(users_router)
router.include_router(finance_router)
router.include_router(depots_router)
router.include_router(monitoring_router)
router.include_router(feedback_router)
router.include_router(tickers_router)
