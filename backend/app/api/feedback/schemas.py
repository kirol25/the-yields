from pydantic import BaseModel


class FeedbackPayload(BaseModel):
    category: str
    message: str
