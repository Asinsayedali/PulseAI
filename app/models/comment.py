from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: int | None = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="tickets.id")
    user_id: int = Field(foreign_key="users.id")
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
