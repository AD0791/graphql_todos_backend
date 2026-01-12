# Graphql FASTAPI Project Demo
---

## Powered by Fastapi and Graphql.

1. Authentication
2. Role based Access
3. JWT (asccess and refresh)
4. CRUD
5. Basic statistics
6. Docker
7. API documentation

## How to run the backend

> UV managed project.

You must sync first (`uv sync`)

TO launch the server without docker, make sure you are at the root dir:

```bash
uv run fastapi dev app/main.py
```

With Docker:

```bash
docker compose up --build
```

