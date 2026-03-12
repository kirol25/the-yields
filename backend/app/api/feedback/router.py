from backend.app.core.limiter import limiter
from fastapi import APIRouter, Header, Request, status
from pydantic import EmailStr

from app.api.feedback import service
from app.api.feedback.schemas import FeedbackPayload

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
    x_user_email: EmailStr | None = Header(default=None),
) -> dict[str, str]:
    """Send a feedback submission as an email via AWS SES."""
    service.submit_feedback(payload, x_user_email)
    return {"status": "sent"}
