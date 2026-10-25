# SprintForge — SDE Portfolio Project

A full-stack project and task management application demonstrating API design, authentication, authorization, relational modeling, automated tests, Docker, CI, and deployment fundamentals.

## Stack
- Frontend: React + TypeScript + Vite
- Backend: Python 3.12 + FastAPI + SQLAlchemy 2
- Database: SQLite locally/tests; PostgreSQL with Docker Compose
- Auth: JWT access tokens + bcrypt password hashing
- Tests: pytest + FastAPI TestClient
- CI: GitHub Actions

## Implemented
- User registration/login and signed JWT access tokens
- Create/list projects owned by the current user
- Project-scoped access control
- Create/list/update/delete tasks with status, priority and optional due date
- Status filtering and pagination
- Pydantic request validation, useful HTTP status codes and API docs
- Responsive React dashboard
- Automated API tests, CI, Dockerfiles and local PostgreSQL Compose setup

## Local development
Requirements: Python 3.12+, Node.js 20+, npm.

### API
```bash
cd server
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
# Windows: Copy-Item .env.example .env
# macOS/Linux: cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs. Health: http://localhost:8000/api/health.

### Frontend (second terminal)
```bash
cd client
# Windows: Copy-Item .env.example .env
# macOS/Linux: cp .env.example .env
npm install
npm run dev
```
Open http://localhost:5173.

### Tests
From `server/` with the virtual environment active:
```bash
pytest -q
```

### Docker Compose
```bash
docker compose up --build
```
Frontend: http://localhost:5173; API: http://localhost:8000; docs: http://localhost:8000/docs.
`docker compose down -v` stops the stack and deletes the local PostgreSQL volume/data.

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Current user |
| GET/POST | `/api/projects` | List/create owned projects |
| GET | `/api/projects/{id}` | Project detail |
| GET/POST | `/api/projects/{id}/tasks` | List/create tasks |
| PATCH | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |

Protected endpoints require `Authorization: Bearer <token>`.

## GitHub setup
Create an empty repository named `sprintforge-sde`, then run from this folder:
```bash
git init
git add .
git commit -m "Build SprintForge SDE portfolio project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sprintforge-sde.git
git push -u origin main
```
Replace `YOUR_USERNAME`. Do not commit `.env` files or secrets.

## Deployment outline
1. Deploy `server/` using its Dockerfile on a Docker-compatible host.
2. Provision managed PostgreSQL and configure `DATABASE_URL`, a long random `JWT_SECRET`, `CLIENT_ORIGIN`, and `ENVIRONMENT=production` in platform secrets.
3. Deploy `client/` as a static Vite build with `VITE_API_URL` set to the deployed API's `/api` URL.
4. Set CORS to the exact frontend origin, enable HTTPS, and verify health, registration, login, project creation, and task updates.
5. Add screenshots and a demo link only after verifying the deployed app.

Docker Compose is for local development. Before production use, add Alembic schema migrations, rate limiting, password reset/email verification, refresh-token rotation, backups, monitoring, and platform-managed secrets. Access tokens expire after two hours. Those additional features are not implemented in this version.

## Interview prep checklist
Be prepared to explain JWT validation, password hashing, ownership checks, SQL indexes, pagination, status filtering, 401 vs 403 vs 404, test isolation, Docker networking, CORS, and why database migrations matter. Add tests for any new feature before claiming it.

## Resume bullets — edit to reflect verified work
**SprintForge | Full-Stack Project Management Platform**
- Built a project and task management app using React, TypeScript, FastAPI, SQLAlchemy, and SQLite/PostgreSQL.
- Implemented JWT authentication, bcrypt password hashing, Pydantic validation, and project-scoped authorization.
- Added API tests and GitHub Actions CI, plus Docker-based local development with PostgreSQL.
- Built a responsive dashboard for project creation, task tracking, status filtering, and progress summaries.

Do not claim production deployment, usage metrics, performance gains, or unimplemented functionality.
