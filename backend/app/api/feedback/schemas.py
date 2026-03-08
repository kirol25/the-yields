from pydantic import BaseModel, Field


class FeedbackPayload(BaseModel):
    category: str = Field(
        description="Category of the feedback"
        " (e.g. 'feedback', 'bug', 'feature request')"
    )
    message: str = Field(description="Detailed message describing the feedback")
