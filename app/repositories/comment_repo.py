from sqlmodel import Session, select
from app.models.comment import Comment


def create(comment: Comment, session: Session) -> Comment:
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def get_by_ticket(ticket_id: int, session: Session) -> list[Comment]:
    statement = select(Comment).where(Comment.ticket_id == ticket_id)
    return list(session.exec(statement).all())
