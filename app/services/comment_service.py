from sqlmodel import Session

from app.core.exceptions import NotFoundError
from app.models.comment import Comment
from app.repositories import comment_repo, ticket_repo
from app.schemas.comment import CommentCreate, CommentResponse


def add_comment(
    ticket_id: int,
    data: CommentCreate,
    user_id: str,
    session: Session,
) -> Comment:
    if not ticket_repo.get_by_id(ticket_id, session):
        raise NotFoundError("Ticket")

    comment = Comment(
        ticket_id=ticket_id,
        user_id=int(user_id),
        content=data.content,
    )
    return comment_repo.create(comment, session)


def list_comments(ticket_id: int, session: Session) -> list[CommentResponse]:
    if not ticket_repo.get_by_id(ticket_id, session):
        raise NotFoundError("Ticket")

    comments = comment_repo.get_by_ticket(ticket_id, session)
    return [CommentResponse.model_validate(c) for c in comments]
