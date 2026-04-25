from pydantic import BaseModel, EmailStr, Field


class MeResponse(BaseModel):
    email: EmailStr = Field(description="The authenticated user's email address")
