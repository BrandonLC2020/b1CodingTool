# FastAPI: Serverless Deployments

## Overview
FastAPI is an ASGI application. Serverless platforms (AWS Lambda, Google Cloud Run, Azure Container Apps) can run it, but they require adapting the standard ASGI lifecycle to fit a stateless, ephemeral execution model.

## ASGI Adapters

### AWS Lambda — Mangum
Use **Mangum** to wrap the FastAPI app as a Lambda handler:

```python
# app/main.py
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# ... routers, middleware, etc.

handler = Mangum(app, lifespan="on")  # "on" runs FastAPI lifespan events
```

Deploy with an API Gateway (HTTP API or REST API) trigger. Mangum translates API Gateway events into ASGI scope/receive/send.

```toml
# pyproject.toml — add mangum
[project.dependencies]
mangum = ">=0.17"
```

### Google Cloud Run / Azure Container Apps
These platforms run a container that receives HTTP traffic directly — no adapter needed. Just run the ASGI server (Uvicorn) inside the container:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --no-dev
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Cloud Run scales to zero between requests, so treat it as serverless for cold-start purposes even though it's container-based.

## Cold Starts

**What is a cold start?** The first request to a new instance (Lambda or container) must initialize the runtime, import your modules, and run your `lifespan` startup logic before handling the request. This adds hundreds of milliseconds to the first request.

**Minimize cold start time:**
- Keep dependencies lean. Every package you import adds to startup time.
- Move expensive imports inside functions if they're not used on every request.
- Use Lambda Snapstart (Java) or Lambda SnapStart alternatives carefully — Python doesn't have a direct equivalent, but keeping the package small helps.
- On Lambda: set memory high enough (1024MB+) — Lambda allocates CPU proportionally to memory. More memory = faster startup.
- On Cloud Run: set `min-instances: 1` for latency-sensitive services to keep a warm instance alive.

## Database Connections — The Critical Problem

Standard SQLAlchemy connection pools are **per-process**. In serverless environments, each cold start creates a new process with a new pool. Under concurrent load, this exhausts Postgres `max_connections` rapidly.

### Solution 1: External Connection Pooler (Recommended for Production)
Place **PgBouncer** or **RDS Proxy** (AWS) between your app and Postgres. The app connects to the pooler, which maintains a fixed pool of real Postgres connections.

```python
# app/core/database.py — serverless-safe engine config
engine = create_async_engine(
    settings.database_url,  # points to PgBouncer/RDS Proxy, not Postgres directly
    pool_size=1,            # one connection per Lambda instance
    max_overflow=0,         # no overflow — pooler handles concurrency
    pool_pre_ping=True,     # verify connection health before use
    pool_recycle=300,       # recycle connections every 5 min
)
```

### Solution 2: NullPool (Simple but Less Efficient)
Disable the connection pool entirely. Each request opens and closes its own connection. Acceptable for low-traffic functions; too slow under load.

```python
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,
)
```

### Solution 3: Serverless-Native Databases
For greenfield projects, consider databases designed for serverless connection patterns:
- **Neon** (serverless Postgres with connection pooling built in)
- **PlanetScale** (serverless MySQL)
- **Supabase** (Postgres with Supavisor pooler)

These handle connection pooling at the infrastructure level, removing the problem entirely.

## Stateless Design

Serverless functions must not rely on in-process state between requests. Any state stored in a module-level variable may or may not exist on the next request (different instance, or instance was recycled).

- **Never** store user sessions, request counts, or mutable cache in module-level variables.
- Use **Redis** (Upstash, ElastiCache) for shared ephemeral state (rate limiting, sessions, caches).
- Use **S3 / GCS / Blob Storage** for file storage — never write to the local filesystem (Lambda's `/tmp` is ephemeral and not shared).
- Use **SQS / Pub/Sub** for background work instead of FastAPI `BackgroundTasks` — background tasks run in the same process and will be killed when the instance is recycled.

## Lifespan Events in Serverless

FastAPI's `lifespan` handler runs **once per cold start**. Use it for:
- Creating the SQLAlchemy engine
- Initializing connection pools
- Warming up caches

Do NOT use it for:
- Running Alembic migrations (run migrations in your CI/CD pipeline, not at startup)
- Long-running initialization that blocks request handling

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on cold start — keep this fast
    app.state.db_engine = create_async_engine(settings.database_url, pool_size=1, max_overflow=0)
    app.state.session_factory = async_sessionmaker(app.state.db_engine, expire_on_commit=False)
    yield
    await app.state.db_engine.dispose()

app = FastAPI(lifespan=lifespan)
```

## Environment Variables & Secrets

- All configuration must come from environment variables — never hardcoded values.
- On AWS Lambda: use **AWS Secrets Manager** or **Parameter Store** for sensitive values; inject them as environment variables at deploy time.
- On Cloud Run: use **Secret Manager** secrets mounted as environment variables.
- Use `pydantic-settings` to validate all env vars at startup so misconfigured deployments fail fast.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")  # .env used locally; real env vars override

    database_url: str
    secret_key: str
    environment: str = "development"

settings = Settings()
```

## Observability

- Use **structured logging** (JSON) — CloudWatch, Cloud Logging, and most APM tools parse JSON logs automatically.
- Add a request ID to every log line using middleware so you can trace a single request across log entries.
- Use **AWS X-Ray** (Lambda) or **Cloud Trace** (Cloud Run) for distributed tracing.
- Set up error reporting (Sentry) before going to production.

```python
# Structured logging middleware example
import logging, json, uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        response = await call_next(request)
        logging.info(json.dumps({
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        }))
        return response
```

## Deployment Checklist
| Item | Why |
|------|-----|
| External connection pooler (PgBouncer / RDS Proxy) | Prevents connection exhaustion under load |
| `pool_size=1, max_overflow=0` on the SQLAlchemy engine | Matches one connection per serverless instance |
| Secrets in environment variables, not source code | Security |
| `min-instances: 1` on latency-sensitive services | Prevents cold starts for user-facing routes |
| Migrations run in CI/CD, not at startup | Startup migration on concurrent cold starts causes race conditions |
| Structured JSON logging | Parseable by cloud log aggregators |
