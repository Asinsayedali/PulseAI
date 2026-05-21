from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.core.security import decode_token
from app.database import get_session
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse
from app.services import auth_service

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(data: SignupRequest, session: Session = Depends(get_session)):
    return auth_service.register_user(data, session)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    return auth_service.login_user(data, session)


@router.post("/logout", status_code=204)
def logout(request: Request):
    token = request.headers.get("Authorization").split(" ", 1)[1]
    payload = decode_token(token)
    auth_service.logout_user(token, payload)
