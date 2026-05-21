from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.database import get_session
from app.models.ticket import TicketPriority, TicketStatus
from app.schemas.common import PaginatedResponse
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.services import ticket_service

router = APIRouter()


@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    data: TicketCreate,
    request: Request,
    session: Session = Depends(get_session),
):
    return ticket_service.create_ticket(data, request.state.user_id, session)


@router.get("", response_model=PaginatedResponse[TicketResponse])
def list_tickets(
    session: Session = Depends(get_session),
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    page: int = 1,
    page_size: int = 20,
):
    return ticket_service.list_tickets(session, status, priority, page, page_size)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, session: Session = Depends(get_session)):
    return ticket_service.get_ticket(ticket_id, session)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    request: Request,
    session: Session = Depends(get_session),
):
    return ticket_service.update_ticket(ticket_id, data, request.state.user_id, session)


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    ticket_service.delete_ticket(ticket_id, request.state.user_id, session)
