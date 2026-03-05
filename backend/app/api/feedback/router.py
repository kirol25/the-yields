from fastapi import APIRouter, Header, status

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
def submit_feedback(
    payload: FeedbackPayload,
    x_user_email: str | None = Header(default=None),
) -> dict[str, str]:
    """Send a feedback submission as an email via AWS SES."""
    service.submit_feedback(payload, x_user_email)
    return {"status": "sent"}
