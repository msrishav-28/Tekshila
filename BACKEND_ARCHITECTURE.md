# Tekshila Backend - 2026 Ready Architecture

## Overview

Modern, agent-driven backend with GitHub OAuth, LangGraph workflows, and real-time streaming capabilities.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js 15    │────▶│   FastAPI API   │────▶│  Agent Workflow │
│   Frontend      │◀────│   (api/main.py) │◀────│  (LangGraph)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Gemini (LLM)   │
                        │   (SQLAlchemy)  │     │                 │
                        └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │     Redis       │
                        │ (Cache/Queue)   │
                        └─────────────────┘
```

## Key Components

### 1. Agent Architecture (`agents/`)

**State-Driven Multi-Agent System using LangGraph:**

```
User Request
    │
    ▼
┌──────────┐
│ Planner  │ ──▶ Creates documentation outline
│  Agent   │
└────┬─────┘
     │
     ▼
┌──────────┐
│ Analyzer │ ──▶ AST parsing, complexity analysis
│  Agent   │
└────┬─────┘
     │
     ▼
┌──────────┐
│  Writer  │ ──▶ Generates documentation
│  Agent   │
└────┬─────┘
     │
     ▼
┌──────────┐
│ Reviewer │ ──▶ Quality check (pass/fail loop)
│  Agent   │
└────┬─────┘
     │
     ▼
   Output
```

**Features:**
- Iterative refinement (up to 3 iterations)
- Streaming output for real-time UI
- State persistence with MemorySaver
- Tool integration (code analysis, GitHub fetch)

### 2. Database (`db/`)

**PostgreSQL + SQLAlchemy 2.0 Async Models:**

| Table | Purpose |
|-------|---------|
| `users` | OAuth accounts, tokens, preferences |
| `projects` | Code projects with GitHub sync |
| `project_files` | AST data, embeddings, metadata |
| `documentation_jobs` | Generation jobs with agent tracking |
| `agent_tasks` | LangGraph state, metrics |
| `integrations` | OAuth connections (GitHub, etc.) |
| `usage_logs` | Billing, analytics, rate limiting |

**Features:**
- Asyncpg for high-performance async queries
- Connection pooling (20 connections, 30 overflow)
- JSONB columns for flexible metadata
- UUID primary keys
- Automatic indexing

### 3. Authentication (`auth/`)

**GitHub OAuth + JWT:**

```
1. User clicks "Connect GitHub"
2. GitHub OAuth redirect
3. Code exchanged for access_token
4. User info fetched from GitHub API
5. User created/updated in database
6. JWT tokens (access + refresh) returned
7. Frontend stores tokens, includes in API calls
```

**Security:**
- 30-minute access tokens
- 7-day refresh tokens
- Encrypted GitHub tokens at rest
- Auto-refresh before expiry

### 4. API (`api/`)

**FastAPI Endpoints:**

| Endpoint | Description |
|----------|-------------|
| `POST /auth/github/callback` | OAuth callback, returns JWT |
| `GET /api/user/me` | Current user profile |
| `GET /api/github/repos` | List GitHub repositories |
| `POST /api/upload` | File upload (multi-file) |
| `POST /api/documentation/generate` | Generate with agents |
| `GET /api/documentation/{id}` | Get generated docs |

**Features:**
- Streaming responses (`text/event-stream`)
- Structured logging with structlog
- GZip compression
- Rate limiting ready
- Usage tracking

## Setup

### 1. Install Dependencies

```bash
# Python 3.11+ required
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp env_template.txt .env
# Edit .env with your credentials
```

### 3. Setup PostgreSQL

```bash
# Create database
createdb tekshila

# Or with Docker
docker run -d \
  --name tekshila-db \
  -e POSTGRES_USER=tekshila \
  -e POSTGRES_PASSWORD=tekshila_password \
  -e POSTGRES_DB=tekshila \
  -p 5432:5432 \
  postgres:15
```

### 4. Setup Redis

```bash
docker run -d \
  --name tekshila-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 5. Run Database Migrations

```bash
# Tables auto-created on first run
python -c "from db.connection import init_db; import asyncio; asyncio.run(init_db())"
```

### 6. Start API Server

```bash
python api/main.py

# Or with uvicorn directly
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Start Frontend

```bash
npm install
npm run dev
```

## GitHub OAuth Setup

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. New OAuth App:
   - **Application name**: Tekshila
   - **Homepage URL**: http://localhost:3000
   - **Authorization callback URL**: http://localhost:3000/auth/github/callback
3. Copy Client ID and Client Secret to `.env`

## Agent Workflow Example

```python
from agents import get_agent_orchestrator, DocumentationType

# Get orchestrator singleton
orchestrator = get_agent_orchestrator()

# Generate documentation
result = await orchestrator.generate_documentation(
    files={
        "main.py": "def main(): pass",
        "utils.py": "def helper(): pass"
    },
    doc_type=DocumentationType.README,
    user_preferences={"style": "technical", "detail_level": "high"}
)

# Result
{
    "success": True,
    "documentation": "# Project Name\n\n## Overview...",
    "analysis": {
        "main.py": {"complexity_score": 3.5, "functions": 1},
        "utils.py": {"complexity_score": 2.0, "functions": 1}
    },
    "iterations": 2
}
```

## Streaming Example

```javascript
const response = await fetch('/api/documentation/generate', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({ files, stream: true })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = new TextDecoder().decode(value);
  const data = JSON.parse(chunk.replace('data: ', ''));
  
  // Update UI in real-time
  updateProgress(data.step);
  appendContent(data.content);
}
```

## Directory Structure

```
tekshila/
├── agents/                     # LangGraph agent architecture
│   ├── __init__.py
│   └── documentation_agent.py  # Multi-agent workflow
├── api/                        # FastAPI application
│   ├── __init__.py
│   └── main.py                # API endpoints, auth, streaming
├── auth/                       # Authentication
│   ├── __init__.py
│   └── security.py            # GitHub OAuth, JWT
├── db/                         # Database
│   ├── __init__.py
│   ├── connection.py          # Async SQLAlchemy setup
│   └── models.py              # SQLAlchemy 2.0 models
├── github_integration.py      # GitHub API wrapper
├── requirements.txt           # Python dependencies
└── env_template.txt           # Environment variables
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.115 |
| Database | PostgreSQL 15 + asyncpg |
| ORM | SQLAlchemy 2.0 |
| Cache | Redis 7 |
| AI/LLM | LangChain + LangGraph |
| LLM Provider | Google Gemini 1.5 Pro |
| Auth | JWT + GitHub OAuth |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers |
| Code Parsing | tree-sitter |
| Logging | structlog |

## Performance

- **Database**: Connection pooling (20 base + 30 overflow)
- **API**: Async endpoints throughout
- **AI**: Streaming responses, token usage tracking
- **Caching**: Redis for sessions and results
- **Files**: Object storage ready (S3/MinIO)

## Security

- JWT tokens with expiry
- Encrypted OAuth tokens at rest
- Input validation with Pydantic
- SQL injection protection (parameterized queries)
- CORS configuration
- Rate limiting ready

## Monitoring

- Structured JSON logging
- LangSmith integration (optional)
- OpenTelemetry support
- Usage tracking for billing
- Agent execution metrics

## License

MIT - Tekshila Team
