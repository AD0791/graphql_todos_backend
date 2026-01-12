# Docker Setup Fixes for GraphQL Todo API

## 🔴 What Was Wrong

### 1. **Dockerfile: uvicorn Not Found** (Critical Bug)

**Original Code (Line 16):**
```bash
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --system --no-cache -r requirements.txt
```

**The Problem:**
The `--system` flag tells UV to install packages to the **system Python**, not into the virtual environment at `/opt/venv`. So when the production stage copies `/opt/venv`, it was copying an **empty** virtual environment without any packages!

**The Fix:**
```bash
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -r requirements.txt   # ← No --system flag!
```

### 2. **Environment Variable Inconsistencies**

**Original `.env`** mixed two naming conventions:
- `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD` (MySQL's native variables)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` (custom variables)

**The Fix:** Use consistent `DB_*` naming throughout and map them to MySQL variables in docker-compose.yml.

### 3. **MySQL User Cannot Be "root"**

**The Problem:** MySQL won't let you create a user named `root` - it's reserved.

**Original docker-compose.yml:**
```yaml
- MYSQL_USER=${DB_USER:-root}  # ← 'root' as default would fail!
```

**The Fix:** Always use a non-root username like `admin` or `graphql_user`.

### 4. **Hardcoded Password in Health Check**

**Original:**
```yaml
test: ["CMD-SHELL", "mysqladmin ping -h localhost -uroot -prootpassword || exit 1"]
```

**The Fix:** Use environment variables:
```yaml
test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-p${DB_ROOT_PASSWORD:-rootpassword}"]
```

---

## 📁 Files to Replace

Replace these files in your project root:

1. `Dockerfile` - Fixed UV installation without --system flag
2. `docker-compose.yml` - Fixed environment variable handling
3. `.env.example` - Template with documentation
4. `.env` - Your actual configuration

---

## 🚀 How to Apply the Fix

```bash
# 1. Stop any running containers
docker compose down

# 2. Remove the old volume (WARNING: This deletes database data!)
docker volume rm graphql_todos_backend_mysql_data

# 3. Replace the files in your project root
#    (Download the files from this output and copy them)

# 4. Rebuild from scratch (no cache to ensure fresh build)
docker compose build --no-cache

# 5. Start the services
docker compose up -d

# 6. Check logs for any errors
docker compose logs -f api

# 7. Verify uvicorn is running
docker compose exec api which uvicorn
# Should output: /opt/venv/bin/uvicorn
```

---

## 🔍 Verification Commands

```bash
# Check if containers are healthy
docker compose ps

# Check API logs
docker compose logs api

# Test health endpoint
curl http://localhost:8000/health

# Access GraphQL Playground
open http://localhost:8000/graphql

# Access Adminer (Database UI)
open http://localhost:8080
# Server: db
# Username: admin
# Password: Pass2pass@91
# Database: todo_db
```

---

## 📝 Understanding the Dockerfile Fix

### Why `--system` Flag Was Wrong

```
┌─────────────────────────────────────────────────────────────┐
│ BUILDER STAGE                                                │
│                                                              │
│  System Python (/usr/local/bin/python)                       │
│       │                                                      │
│       └──► Packages installed HERE with --system flag        │
│                                                              │
│  Virtual Env (/opt/venv)                                     │
│       │                                                      │
│       └──► EMPTY! No packages!                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ PRODUCTION STAGE                                             │
│                                                              │
│  COPY --from=builder /opt/venv /opt/venv                     │
│       │                                                      │
│       └──► Copies EMPTY virtual environment!                 │
│                                                              │
│  PATH="/opt/venv/bin:$PATH"                                  │
│       │                                                      │
│       └──► uvicorn NOT FOUND! 💥                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### The Fix: Remove `--system` Flag

```
┌─────────────────────────────────────────────────────────────┐
│ BUILDER STAGE                                                │
│                                                              │
│  Virtual Env (/opt/venv)                                     │
│       │                                                      │
│       └──► Packages installed HERE (no --system)             │
│           ├── uvicorn                                        │
│           ├── fastapi                                        │
│           ├── strawberry-graphql                             │
│           └── ... all dependencies                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ PRODUCTION STAGE                                             │
│                                                              │
│  COPY --from=builder /opt/venv /opt/venv                     │
│       │                                                      │
│       └──► Copies FULL virtual environment with packages!    │
│                                                              │
│  PATH="/opt/venv/bin:$PATH"                                  │
│       │                                                      │
│       └──► uvicorn FOUND at /opt/venv/bin/uvicorn ✅         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Notes

Before deploying to production:

1. **Generate a secure SECRET_KEY:**
   ```bash
   openssl rand -hex 32
   ```

2. **Use strong database passwords:**
   ```bash
   openssl rand -base64 24
   ```

3. **Set DEBUG=false in production**

4. **Update CORS_ORIGINS to only allow your frontend URL**

5. **Change the default superadmin credentials**
