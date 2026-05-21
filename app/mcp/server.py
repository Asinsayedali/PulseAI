import json
from fastmcp import FastMCP
from app.config import settings
from app.mcp.client import PulseDeskClient

mcp = FastMCP("PulseDesk AI")

client = PulseDeskClient(
    base_url=settings.MCP_API_BASE_URL,
    email=settings.MCP_SERVICE_EMAIL,
    password=settings.MCP_SERVICE_PASSWORD,
)


@mcp.tool()
def search_tickets(
    status: str | None = None,
    priority: str | None = None,
    page: int = 1,
) -> str:
    """
    Search and list tickets from PulseDesk.
    Optionally filter by status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
    or priority (LOW, MEDIUM, HIGH, CRITICAL).
    Returns a paginated list of tickets.
    """
    result = client.search_tickets(status=status, priority=priority, page=page)
    tickets = result.get("items", [])

    if not tickets:
        return "No tickets found matching the given filters."

    lines = [f"Found {result['total']} ticket(s). Page {result['page']}:\n"]
    for t in tickets:
        lines.append(
            f"[#{t['id']}] {t['title']}\n"
            f"  Status: {t['status']}  |  Priority: {t['priority']}\n"
            f"  AI Summary: {t.get('ai_summary') or 'Not yet analysed'}\n"
        )

    return "\n".join(lines)


@mcp.tool()
def get_ticket(ticket_id: int) -> str:
    """
    Retrieve full details of a single ticket by its ID.
    Includes AI-generated summary, category, and priority suggestion.
    """
    ticket = client.get_ticket(ticket_id)

    return (
        f"Ticket #{ticket['id']}: {ticket['title']}\n"
        f"Status:    {ticket['status']}\n"
        f"Priority:  {ticket['priority']}\n"
        f"Created by user ID: {ticket['created_by']}\n\n"
        f"Description:\n{ticket['description']}\n\n"
        f"--- AI Analysis ---\n"
        f"Summary:             {ticket.get('ai_summary') or 'Pending'}\n"
        f"Category:            {ticket.get('ai_category') or 'Pending'}\n"
        f"Priority suggestion: {ticket.get('ai_priority_suggestion') or 'Pending'}\n"
    )
