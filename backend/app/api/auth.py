import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from app import settings


def verify_access_token(token: str) -> dict:
    """Verify a Cognito access token by calling GetUser.

    Returns ``{"email": str, "is_premium": bool}``.
    Raises HTTP 401 if the token is invalid or expired.
    Raises HTTP 502 if the Cognito service is unreachable.
    """
    client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION)
    try:
        response = client.get_user(AccessToken=token)
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in ("NotAuthorizedException", "UserNotFoundException"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service unavailable",
        )

    attrs = {a["Name"]: a["Value"] for a in response.get("UserAttributes", [])}
    email = attrs.get("email", "")
    is_premium = attrs.get("custom:is_premium", "false").lower() == "true"
    return {"email": email, "is_premium": is_premium}
