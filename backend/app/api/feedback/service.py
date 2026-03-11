import logging
from datetime import UTC, datetime

import boto3
from fastapi import HTTPException, status

from app.api.feedback.schemas import FeedbackPayload
from app.config import get_settings

logger = logging.getLogger("the-yields")

_CATEGORY_LABELS = {
    "feedback": "Feedback",
    "bug": "Bug Report",
    "feature": "Feature Request",
}

_ANONYMOUS = "anonymous"


def submit_feedback(
    payload: FeedbackPayload, email: str | None = None
) -> dict[str, str]:
    """Send a feedback submission as an email via AWS SES."""
    sender = email or _ANONYMOUS
    category_label = _CATEGORY_LABELS.get(payload.category, payload.category)
    subject = f"[{category_label}] the-yields feedback"
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    body = (
        f"Category: {category_label}\n"
        f"From: {sender}\n"
        f"Submitted: {timestamp}\n"
        f"\n"
        f"{payload.message}\n"
    )

    _send_email(subject, body, sender)


def _send_email(subject: str, body: str, sender: str) -> None:
    """Helper to send an email via AWS SES with the given *subject* and *body*."""
    settings = get_settings()

    try:
        client = boto3.client("ses", region_name=settings.AWS_REGION)
        client.send_email(
            Source=settings.FEEDBACK_FROM_EMAIL,
            Destination={"ToAddresses": [settings.FEEDBACK_TO_EMAIL]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
            ReplyToAddresses=[sender] if sender != _ANONYMOUS else [],
        )
    except Exception as exc:
        logger.error("SES send_email failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send feedback email.",
        ) from exc
