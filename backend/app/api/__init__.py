from fastapi import APIRouter

from .feedback.router import router as feedback_router
from .finance.router import router as finance_router
from .monitoring.router import router as monitoring_router

router = APIRouter()
router.include_router(finance_router)
router.include_router(monitoring_router)
router.include_router(feedback_router)
