from fastapi import APIRouter, Request, status

from app.api.feedback import service
from app.api.feedback.schemas import FeedbackPayload
from app.api.finance.dependencies import AuthContextDep
from app.core.limiter import limiter

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post(
    "/feedback",
    responses={
        status.HTTP_201_CREATED: {"description": "Feedback sent successfully."},
        status.HTTP_502_BAD_GATEWAY: {"description": "Failed to send feedback email."},
    },
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback",
    description="Sends the feedback message via AWS SES to the configured recipient.",
)
@limiter.limit("5/hour")
def submit_feedback(
    request: Request,
    payload: FeedbackPayload,
    ctx: AuthContextDep,
) -> dict[str, str]:
    """Send a feedback submission as an email via AWS SES."""
    service.submit_feedback(payload, ctx["email"])
    return {"status": "sent"}
