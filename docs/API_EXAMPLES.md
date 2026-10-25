# API quick examples

Base URL for local development: `http://localhost:8000/api`.

## Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"Demo User","email":"demo@example.com","password":"a-long-demo-password"}'
```

Copy the `token` field from the response for the protected calls below. Never publish a real token.

## Create a project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H 'Authorization: Bearer YOUR_TOKEN' -H 'Content-Type: application/json' \
  -d '{"name":"Interview Prep","description":"SDE preparation tasks"}'
```

## Create a task
```bash
curl -X POST http://localhost:8000/api/projects/1/tasks \
  -H 'Authorization: Bearer YOUR_TOKEN' -H 'Content-Type: application/json' \
  -d '{"title":"Practice graph problems","priority":"HIGH"}'
```

## Filter and paginate tasks
```bash
curl 'http://localhost:8000/api/projects/1/tasks?status=TODO&page=1&limit=20' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```
