import json
from groq import Groq
from sqlmodel import Session
import app.models  # noqa: F401 — registers all models so FK resolution works
from app.config import settings
from app.database import engine
from app.repositories import ticket_repo
from app.utils.logger import logger
from app.workers.celery_app import celery_app

SYSTEM_PROMPT = """You are a support ticket triage assistant.
Analyze the ticket and return ONLY a JSON object with exactly these keys:
- "summary": one concise sentence describing the issue
- "category": exactly one of [Authentication, Billing, Infrastructure, UI Bug, Database, Performance, Other]
- "priority_suggestion": exactly one of [LOW, MEDIUM, HIGH, CRITICAL]
No extra text, no markdown, just the JSON object."""


@celery_app.task(name="tasks.process_ticket_with_ai", bind=True, max_retries=3)
def process_ticket_with_ai(self, ticket_id: int):
    logger.info("ai_task_started", ticket_id=ticket_id)

    with Session(engine) as session:
        ticket = ticket_repo.get_by_id(ticket_id, session)
        if not ticket:
            logger.warning("ai_task_ticket_not_found", ticket_id=ticket_id)
            return

        try:
            client = Groq(api_key=settings.GROQ_API_KEY)

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Title: {ticket.title}\nDescription: {ticket.description}",
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            raw = response.choices[0].message.content
            ai_data = json.loads(raw)

            ticket_repo.update_ai_fields(ticket_id, ai_data, session)
            logger.info("ai_task_completed", ticket_id=ticket_id, category=ai_data.get("category"))

        except Exception as exc:
            logger.error("ai_task_failed", ticket_id=ticket_id, error=str(exc))
            raise self.retry(exc=exc, countdown=60)
