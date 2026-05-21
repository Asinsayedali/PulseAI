from sqlmodel import Session
from app.utils.redis_client import redis_client
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repo
from datetime import datetime, timezone
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse


def register_user(data: SignupRequest, session: Session) -> TokenResponse:
    if user_repo.get_by_email(data.email, session):
        raise ConflictError("Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    user = user_repo.create_user(user, session)
    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


def login_user(data: LoginRequest, session: Session) -> TokenResponse:
    user = user_repo.get_by_email(data.email, session)
    if not user or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)

def logout_user(token: str, payload: dict) -> None:
    ttl_seconds = int(payload["exp"] - datetime.now(timezone.utc).timestamp())
    redis_client.setex(f"blacklist:{token}", ttl_seconds, "1")
