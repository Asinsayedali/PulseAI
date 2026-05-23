from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.database import get_session
from app.schemas.comment import CommentCreate, CommentResponse
from app.services import comment_service

router = APIRouter()


@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=201)
def add_comment(
    ticket_id: int,
    data: CommentCreate,
    request: Request,
    session: Session = Depends(get_session),
):
    return comment_service.add_comment(ticket_id, data, request.state.user_id, session)


@router.get("/{ticket_id}/comments", response_model=list[CommentResponse])
def list_comments(ticket_id: int, session: Session = Depends(get_session)):
    return comment_service.list_comments(ticket_id, session)
