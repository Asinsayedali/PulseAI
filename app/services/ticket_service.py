from datetime import datetime, timezone

from sqlmodel import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.repositories import ticket_repo
from app.schemas.common import PaginatedResponse
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate


def create_ticket(data: TicketCreate, user_id: str, session: Session) -> Ticket:
    ticket = Ticket(
        title=data.title,
        description=data.description,
        created_by=int(user_id),
    )
    ticket = ticket_repo.create(ticket, session)

    # Enqueue AI analysis — worker will populate ai_summary, ai_category, ai_priority_suggestion
    # Imported here to avoid circular imports at module load time
    from app.workers.tasks.ai_tasks import process_ticket_with_ai
    process_ticket_with_ai.delay(ticket.id)

    return ticket


def get_ticket(ticket_id: int, session: Session) -> Ticket:
    ticket = ticket_repo.get_by_id(ticket_id, session)
    if not ticket:
        raise NotFoundError("Ticket")
    return ticket


def list_tickets(
    session: Session,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[TicketResponse]:
    tickets, total = ticket_repo.list_all(session, status, priority, page, page_size)
    return PaginatedResponse(
        items=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        page_size=page_size,
    )


def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    user_id: str,
    session: Session,
) -> Ticket:
    ticket = ticket_repo.get_by_id(ticket_id, session)
    if not ticket:
        raise NotFoundError("Ticket")
    if ticket.created_by != int(user_id):
        raise ForbiddenError("You do not own this ticket")

    # Only update fields that were explicitly sent — None means "not provided"
    if data.status is not None:
        ticket.status = data.status
    if data.priority is not None:
        ticket.priority = data.priority
    if data.assigned_to is not None:
        ticket.assigned_to = data.assigned_to

    ticket.updated_at = datetime.now(timezone.utc)
    return ticket_repo.update(ticket, session)


def delete_ticket(ticket_id: int, user_id: str, session: Session) -> None:
    ticket = ticket_repo.get_by_id(ticket_id, session)
    if not ticket:
        raise NotFoundError("Ticket")
    if ticket.created_by != int(user_id):
        raise ForbiddenError("You do not own this ticket")
    ticket_repo.delete(ticket, session)
