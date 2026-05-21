# PulseDesk AI

AI-powered ticket management backend built with FastAPI. When a ticket is created, a background worker automatically calls the Groq API (Llama model) to generate a plain-English summary, classify the category, and suggest a priority — all stored back on the ticket without blocking the HTTP response.

An MCP server ships alongside the REST API, letting Claude Desktop query tickets using natural language.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 16 via SQLModel (SQLAlchemy + Pydantic merged) |
| Auth | JWT — validated in ASGI middleware, not route-level |
| Background jobs | Celery + Redis |
| AI analysis | Groq API (Llama 3.1) |
| MCP server | FastMCP |
| HTTP client (MCP) | httpx |
| Package manager | uv |

---

## Architecture

```
Request
  └─► AuthMiddleware       — validates JWT, attaches user_id to request.state
        └─► LoggingMiddleware  — structured JSON request/response logs
              └─► Controller   — HTTP only: parse request, call service, return response
                    └─► Service    — business logic, raises domain errors
                          └─► Repository  — raw SQL queries via SQLModel session
```

On ticket creation the service immediately enqueues a Celery task and returns the ticket (AI fields are `null`). The worker picks it up from Redis, calls Groq, and writes `ai_summary`, `ai_category`, and `ai_priority_suggestion` back to the database.

---

## Database Schema

### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | integer PK | auto-increment |
| `email` | varchar | unique, indexed |
| `hashed_password` | varchar | bcrypt |
| `is_admin` | boolean | default false |
| `created_at` | timestamptz | UTC |

### `tickets`

| Column | Type | Notes |
|---|---|---|
| `id` | integer PK | auto-increment |
| `title` | varchar | |
| `description` | text | |
| `status` | enum | `OPEN` / `IN_PROGRESS` / `RESOLVED` / `CLOSED` |
| `priority` | enum | `LOW` / `MEDIUM` / `HIGH` / `CRITICAL` |
| `created_by` | integer FK → `users.id` | |
| `assigned_to` | integer FK → `users.id` | nullable |
| `ai_summary` | text | null until worker runs |
| `ai_category` | text | null until worker runs |
| `ai_priority_suggestion` | text | null until worker runs |
| `created_at` | timestamptz | UTC |
| `updated_at` | timestamptz | UTC |

### `comments`

| Column | Type | Notes |
|---|---|---|
| `id` | integer PK | auto-increment |
| `ticket_id` | integer FK → `tickets.id` | |
| `user_id` | integer FK → `users.id` | |
| `content` | text | |
| `created_at` | timestamptz | UTC |

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- A [Groq API key](https://console.groq.com/)

---

## Setup

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd pulsedesk-ai
```

### 2. Create `.env`

Copy the example and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
# Docker Compose wires these hostnames automatically
DATABASE_URL=postgresql://pulsedesk:pulsedesk@postgres:5432/pulsedesk
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-long-random-secret-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# From https://console.groq.com/
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.1-8b-instant

# MCP service account — create this user via /auth/signup after first boot
MCP_SERVICE_EMAIL=mcp@pulsedesk.internal
MCP_SERVICE_PASSWORD=strong-password-here
MCP_API_BASE_URL=http://localhost:8000

DEBUG=false
```

### 3. Start all services

```bash
docker compose up --build
```

This starts four containers: `api` (port 8000), `worker` (Celery), `postgres` (port 5432), `redis` (port 6379).

### 4. Verify

```bash
curl http://localhost:8000/
# {"status": "ok"}
```

Swagger UI is at [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Register the MCP service account

The MCP server authenticates to the API with a dedicated service account. Create it once:

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "mcp@pulsedesk.internal", "password": "strong-password-here"}'
```

Use the same email and password you set as `MCP_SERVICE_EMAIL` / `MCP_SERVICE_PASSWORD` in `.env`.

---

## API Endpoints

All routes are under `/api/v1`. Protected routes require `Authorization: Bearer <token>`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/signup` | public | Register a new user |
| POST | `/auth/login` | public | Get a JWT token |
| POST | `/auth/logout` | required | Invalidate token (Redis blacklist) |
| GET | `/tickets` | required | List tickets (filter by status, priority) |
| POST | `/tickets` | required | Create ticket + enqueue AI analysis |
| GET | `/tickets/{id}` | required | Get single ticket with AI fields |
| PUT | `/tickets/{id}` | required | Update ticket |
| DELETE | `/tickets/{id}` | required | Delete ticket |

---

## MCP Server

The MCP server exposes two tools that Claude Desktop can call:

| Tool | Description |
|---|---|
| `search_tickets` | List tickets, optionally filtered by status or priority |
| `get_ticket` | Get full details of a ticket by ID, including AI analysis |

### Local setup (MCP only)

The MCP server only needs a small subset of dependencies. Use the dedicated requirements file:

```bash
uv venv
uv pip install -r requirements-mcp.txt
```

### Test with the inspector

```bash
uv run fastmcp dev inspector run_mcp.py
```

This opens the MCP Inspector in your browser where you can call tools interactively. The FastAPI server must be running (`docker compose up`) for the tools to return data.

### Connect to Claude Desktop

Open the Claude Desktop config file:

```bash
open ~/Library/Application\ Support/Claude/
```

Edit (or create) `claude_desktop_config.json` and add the `pulsedesk` server under `mcpServers`:

```json
{
  "mcpServers": {
    "pulsedesk": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/pulsedesk-ai",
        "run",
        "python",
        "run_mcp.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/pulsedesk-ai` with the actual path on your machine.

**Quit and reopen Claude Desktop.** You will see a hammer icon (🔨) in the chat input confirming the tools are connected. The FastAPI server must be running for tool calls to succeed.

---

## Development

### Running tests

```bash
uv run pytest
```

### Watching Celery worker logs

```bash
docker compose logs -f worker
```

### Rebuilding after dependency changes

```bash
docker compose up --build
```
