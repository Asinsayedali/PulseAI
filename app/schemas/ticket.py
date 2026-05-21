from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.ticket import TicketStatus, TicketPriority


class TicketCreate(BaseModel):
    title: str
    description: str


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_to: int | None = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    created_by: int
    assigned_to: int | None
    ai_summary: str | None
    ai_category: str | None
    ai_priority_suggestion: str | None
    created_at: datetime
    updated_at: datetime
