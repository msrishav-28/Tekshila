# Tekshila

[![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Three.js](https://img.shields.io/badge/Three.js-black?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org/)
<br>
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com/langgraph)

AI-powered code documentation with cinematic engineering precision. Transform your codebase into comprehensive documentation using agent-driven workflows.

[Live Demo](https://tekshila.dev) | [Documentation](https://docs.tekshila.dev) | [GitHub](https://github.com/your-org/tekshila)

---

## Features

- **Agent Architecture**: Multi-agent system using LangGraph for intelligent documentation generation
- **GitHub OAuth**: Secure authentication with GitHub integration
- **Real-time Streaming**: Live documentation generation with Server-Sent Events
- **Vector Search**: Semantic code search using ChromaDB and embeddings
- **3D Visualizations**: Interactive Three.js components with glass morphism design
- **Modern Stack**: Next.js 15, React 19, FastAPI, PostgreSQL, Redis

---

## Architecture

```
Frontend (Next.js 15)
├── React 19 + TypeScript
├── Three.js (R3F) for 3D visualizations
├── Framer Motion for animations
├── Tailwind CSS for styling
└── Lucide React for icons

Backend (Python)
├── FastAPI 0.115 with async endpoints
├── SQLAlchemy 2.0 + PostgreSQL
├── Redis for caching and queues
├── LangGraph agent workflows
├── ChromaDB for vector storage
└── GitHub API integration
```

---

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-org/tekshila.git
cd tekshila
```

2. **Install frontend dependencies**

```bash
npm install
```

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp env_template.txt .env
# Edit .env with your credentials
```

5. **Setup database**

```bash
# Using Docker
docker run -d --name tekshila-db -p 5432:5432 \
  -e POSTGRES_USER=tekshila \
  -e POSTGRES_PASSWORD=tekshila_password \
  -e POSTGRES_DB=tekshila \
  postgres:15

docker run -d --name tekshila-redis -p 6379:6379 redis:7

# Initialize tables
python -c "from db.connection import init_db; import asyncio; asyncio.run(init_db())"
```

6. **Start services**

```bash
# Terminal 1 - API
python api/main.py

# Terminal 2 - Frontend
npm run dev
```

7. **Access the application**

Open [http://localhost:3000](http://localhost:3000)

---

## Configuration

### GitHub OAuth Setup

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Tekshila
   - **Homepage URL**: http://localhost:3000
   - **Authorization callback URL**: http://localhost:3000/auth/github/callback
4. Copy Client ID and Client Secret to `.env`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | Required |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | Required |
| `SECRET_KEY` | JWT signing key | Required |

---

## API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/github/callback` | POST | Exchange GitHub code for JWT |
| `/auth/refresh` | POST | Refresh access token |

### Documentation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documentation/generate` | POST | Generate docs (supports streaming) |
| `/api/documentation/jobs` | GET | List documentation jobs |
| `/api/documentation/{id}` | GET | Get specific documentation |

### Projects

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects` | GET | List user projects |
| `/api/projects` | POST | Create new project |
| `/api/github/repos` | GET | List GitHub repositories |

---

## Agent Workflow

Tekshila uses a multi-agent system for documentation generation:

1. **Planner Agent**: Analyzes code structure and creates documentation outline
2. **Analyzer Agent**: Performs AST parsing and complexity analysis
3. **Writer Agent**: Generates documentation content using Gemini 1.5 Pro
4. **Reviewer Agent**: Quality checks and iterative refinement

The agents communicate through a state graph (LangGraph) with persistence and streaming support.

---

## Project Structure

```
tekshila/
├── app/                        # Next.js 15 application
│   ├── globals.css            # Design system (Prism)
│   ├── layout.tsx             # Root layout with auth
│   ├── page.tsx               # Landing page
│   ├── dashboard/             # Dashboard routes
│   └── auth/github/callback/  # OAuth callback
├── components/                # React components
│   ├── GlassCard.tsx          # Glass morphism card
│   ├── MagneticButton.tsx     # Magnetic hover button
│   ├── HeroScene.tsx          # Three.js scene
│   └── GlassSidebar.tsx       # Navigation sidebar
├── hooks/                     # Custom React hooks
│   └── useAuth.tsx            # Authentication hook
├── lib/                       # Utilities
│   ├── api.ts                 # API client
│   └── utils.ts               # Helper functions
├── agents/                    # LangGraph agents
│   └── documentation_agent.py # Multi-agent workflow
├── api/                       # FastAPI application
│   └── main.py                # API endpoints
├── auth/                      # Authentication
│   └── security.py            # OAuth and JWT
├── db/                        # Database
│   ├── models.py              # SQLAlchemy models
│   └── connection.py          # Async connection
├── package.json               # Node dependencies
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Development

### Frontend

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

### Backend

```bash
# Run API server
python api/main.py

# Or with uvicorn
uvicorn api.main:app --reload --port 8000
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head
```

---

## Testing

```bash
# Backend tests
pytest

# Frontend tests
npm test
```

---

## Deployment

### Docker

```bash
docker-compose up -d
```

### Vercel (Frontend)

```bash
npm i -g vercel
vercel --prod
```

### Railway/Render (Backend)

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [LangChain](https://langchain.com/) - LLM orchestration
- [Three.js](https://threejs.org/) - 3D graphics
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework

---

Built with precision by the Tekshila Team.
