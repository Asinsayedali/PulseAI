from sqlmodel import Session, select, func
from app.models.ticket import Ticket, TicketStatus, TicketPriority


def create(ticket: Ticket, session: Session) -> Ticket:
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def get_by_id(ticket_id: int, session: Session) -> Ticket | None:
    return session.get(Ticket, ticket_id)


def list_all(
    session: Session,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Ticket], int]:
    statement = select(Ticket)

    if status:
        statement = statement.where(Ticket.status == status)
    if priority:
        statement = statement.where(Ticket.priority == priority)

    total = session.exec(select(func.count()).select_from(statement.subquery())).one()

    statement = statement.offset((page - 1) * page_size).limit(page_size)
    tickets = list(session.exec(statement).all())

    return tickets, total


def update(ticket: Ticket, session: Session) -> Ticket:
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def delete(ticket: Ticket, session: Session) -> None:
    session.delete(ticket)
    session.commit()


def update_ai_fields(ticket_id: int, ai_data: dict, session: Session) -> None:
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        return
    ticket.ai_summary = ai_data.get("summary")
    ticket.ai_category = ai_data.get("category")
    ticket.ai_priority_suggestion = ai_data.get("priority_suggestion")
    session.add(ticket)
    session.commit()
