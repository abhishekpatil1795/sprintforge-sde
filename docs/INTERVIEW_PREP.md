# SprintForge Interview Preparation

Use this guide to prepare to explain the code you actually ran and tested. Do not memorize answers without understanding the implementation.

## Architecture in 60 seconds

The React + TypeScript client calls a FastAPI REST API. FastAPI validates request bodies with Pydantic, dependency injection provides a SQLAlchemy session and resolves the authenticated user, and SQLAlchemy reads/writes the relational database. Passwords are stored as bcrypt hashes. The API issues signed JWT access tokens and checks their signature and expiry on protected routes. Projects and tasks are scoped to the current user's ownership; unauthorized resource lookups return 404 to avoid confirming another user's resource exists. Tests use a separate SQLite database and exercise API requests through FastAPI's TestClient.

## Explain these design choices

### Why FastAPI?
- Type hints and Pydantic models make request/response contracts explicit.
- Automatic OpenAPI documentation helps inspect and test endpoints.
- Dependency injection centralizes database-session and current-user handling.

### Why SQLAlchemy and relational tables?
- Projects have an owner; tasks belong to projects. Foreign keys encode these relationships.
- Indexes support owner filtering and the common `(project_id, status)` task query.
- Relational constraints and transactions protect consistency better than manually coordinated JSON files.

### Why hash passwords?
Never store plaintext passwords. bcrypt is a password-hashing algorithm designed to make guessing expensive. A password hash is not encryption and cannot be decrypted back to the original password.

### How JWT authentication works here
1. Registration/login verifies input and returns a signed access token.
2. The client sends it in `Authorization: Bearer <token>`.
3. The API verifies signature and expiry, reads the `sub` user ID, and loads that user.
4. Each resource endpoint separately checks ownership. A valid token alone does not grant access to every project.

The current app uses two-hour access tokens and does not implement refresh-token rotation or revocation. Explain that trade-off honestly.

### 401 vs 403 vs 404
- 401: credentials are absent, invalid, or expired.
- 403: authenticated user is known but forbidden from an action; this project often uses 404 for inaccessible resources to avoid leaking their existence.
- 404: requested or visible resource is not found.

### Why pagination?
Returning every row becomes expensive as data grows. `page` and `limit` bound the response; `limit` is capped at 100. Offset pagination is easy to implement but can become slower for deep pages and can shift under concurrent writes. Cursor pagination is a possible future improvement.

### What does CI do?
GitHub Actions installs the Python dependencies, runs API tests, then installs frontend dependencies and runs a production build. CI catches regressions before merging; it does not prove the app is secure or production-ready.

## Important limitations to acknowledge

- `Base.metadata.create_all()` is used for simple local startup. Production schema evolution should use Alembic migrations.
- Rate limiting, email verification, password reset, refresh-token rotation, audit logs, and automated backups are not implemented.
- The default development secret is not safe for deployment. Configure a long random `JWT_SECRET` through the host's secret manager.
- Docker Compose credentials are local-only placeholders and must not be reused in a public deployment.
- The app currently models project ownership, not team membership or invitations.
- Tests cover core API flows, but frontend and browser-level end-to-end tests are not included.

## Practice questions

1. **How would you prevent a user from reading another user's tasks?**
   Resolve the task through a join to its project and filter by the authenticated user's ID. Do not rely on the client hiding links or buttons.
2. **What is the N+1 query problem?**
   It occurs when code fetches a collection and then issues an additional query for each row. Inspect query counts and use eager loading or aggregation where appropriate. Project counts here are queried individually and could be optimized for large project lists.
3. **How would you make schema changes safely?**
   Use Alembic migrations, deploy backward-compatible changes first, migrate data where needed, and avoid destructive changes until all deployed code no longer depends on old columns.
4. **How would you test access control?**
   Create two users, create a project as one, then assert the other receives 404 for project detail, task listing, task update, and task deletion.
5. **What would you change for higher traffic?**
   Add proper migrations, structured logging/metrics, rate limiting, database connection pool tuning, query analysis, cursor pagination where appropriate, and load tests. Scale stateless API replicas behind a load balancer and keep secrets/database externalized.
6. **What is the difference between authentication and authorization?**
   Authentication establishes who the caller is; authorization decides which resources/actions that identity may access.
7. **Why not trust `owner_id` from the request body?**
   It allows a client to claim ownership of another user's resource. The API derives the owner ID from the verified current user.
8. **How would you handle concurrent task updates?**
   Consider optimistic locking/version columns or transactional conflict handling if lost updates become a real concern.

## Before an interview

- Run the app from a clean clone following the README.
- Run `pytest -q` and `npm run build` locally.
- Exercise every endpoint in `/docs` and test a second user for cross-account access.
- Draw the `User -> Project -> Task` relationship model from memory.
- Be able to explain one bug you encountered, how you reproduced it, and how you tested the fix.
- Deploy a live demo only after configuring production secrets, database, CORS, HTTPS, and backups appropriately.
