from app.api.users.schemas import MeResponse


class UserService:
    def get_me(self, email: str) -> MeResponse:
        return MeResponse(email=email)
