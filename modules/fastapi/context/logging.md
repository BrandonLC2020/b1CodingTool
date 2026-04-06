# FastAPI: Logging Best Practices

## Philosophy

Good logs answer two questions without any additional context: **what happened**, and **why it matters**. Every log line should be self-contained enough that a human or AI agent reading it in isolation — with no knowledge of the codebase — can understand the event and act on it.

- **Structured over narrative.** Key-value pairs beat prose. `{"event": "db_query_slow", "table": "orders", "duration_ms": 4200, "query": "SELECT ..."}` is queryable; `"Slow query on orders"` is not.
- **Correlation IDs everywhere.** Every request gets a UUID. Every log line for that request carries it. This is the thread that lets you reconstruct a full request trace from fragmented log lines.
- **Async-safe context.** Python's `logging` module uses thread-local storage — in an async app, you need `contextvars`-based context binding so log context doesn't leak between concurrent requests.

## Log Levels — When to Use Each

| Level | Use for |
|-------|---------|
| `DEBUG` | Internal state, SQL query text, deserialized payloads. Disabled in production by default. |
| `INFO` | Normal lifecycle events: request received/completed, background task started, user authenticated. |
| `WARNING` | Unexpected but recoverable: retry triggered, deprecated endpoint called, config fallback used. |
| `ERROR` | A specific operation failed: DB write failed, external API returned 5xx, unhandled exception in a route. |
| `CRITICAL` | Application cannot continue: DB unreachable, required env var missing, unrecoverable startup failure. |

## Setup: structlog

`structlog` integrates with Python's `logging` module and produces JSON output suitable for log aggregators (CloudWatch, Datadog, Loki).

```bash
uv add structlog
```

```python
# app/core/logging.py
import logging
import structlog

def configure_logging(debug: bool = False) -> None:
    shared_processors = [
        structlog.contextvars.merge_contextvars,      # injects request-scoped context
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if debug:
        renderer = structlog.dev.ConsoleRenderer()    # human-friendly in dev
    else:
        renderer = structlog.processors.JSONRenderer()  # machine-readable in prod

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # SQLAlchemy query logging — debug only
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if debug else logging.WARNING
    )
```

Call from `main.py`:
```python
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging(debug=settings.debug)
```

## Correlation IDs via Middleware

Bind a `request_id` to every request using `contextvars` so all log calls within that request automatically include it.

```python
# app/middleware/logging.py
import time
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import clear_contextvars, bind_contextvars

logger = structlog.get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        clear_contextvars()
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        logger.info("request_started")
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_unhandled_exception")
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        bind_contextvars(status_code=response.status_code, duration_ms=duration_ms)
        level = "warning" if response.status_code >= 400 else "info"
        getattr(logger, level)("request_finished")

        response.headers["x-request-id"] = request_id
        return response
```

Register in `main.py`:
```python
app.add_middleware(RequestLoggingMiddleware)
```

## Logging in Application Code

```python
import structlog

logger = structlog.get_logger(__name__)

async def create_order(db: AsyncSession, user_id: int, payload: OrderCreate) -> Order:
    log = logger.bind(user_id=user_id, item_count=len(payload.items))
    log.info("order_creation_started")

    try:
        order = await order_repo.create(db, user_id=user_id, items=payload.items)
    except IntegrityError as e:
        log.error("order_creation_failed", reason="db_integrity_error", detail=str(e))
        raise

    log.info("order_created", order_id=str(order.id), total=float(order.total))
    return order
```

## Logging Dependency Injection

Inject a pre-bound logger as a FastAPI dependency so route handlers get a logger already enriched with authenticated user context:

```python
# app/core/dependencies.py
import structlog
from structlog.contextvars import bind_contextvars

async def get_logger(current_user: User = Depends(get_current_user)):
    bind_contextvars(user_id=str(current_user.id), user_email=current_user.email)
    return structlog.get_logger()
```

```python
@router.post("/orders/", response_model=OrderResponse, status_code=201)
async def create_order(
    payload: OrderCreate,
    db: DBSession,
    logger=Depends(get_logger),
):
    logger.info("order_endpoint_called", item_count=len(payload.items))
    return await order_service.create_order(db, payload)
```

## What to Log (and When)

**Request lifecycle:**
- Request received (method, path, user_id once authenticated)
- Request completed (status_code, duration_ms)
- Every unhandled exception (full traceback)

**Business events:**
- Authentication success and failure (failure reason, never the password)
- State transitions on important entities (`order.status: pending → paid`)
- Every external HTTP call (method, url, status_code, duration_ms)

**Database:**
- Slow queries (configure SQLAlchemy to log queries exceeding a threshold)
- Connection pool exhaustion or timeout

**Background tasks:**
- Task enqueued (task_name, task_id, arguments summary)
- Task started, succeeded, failed (with duration and error detail)

**Errors:**
- Every `except` block that suppresses an exception must log it at WARNING or ERROR
- Never silently swallow exceptions

## What NOT to Log

- Passwords, tokens, API keys, secrets — ever
- Raw `Authorization` header values
- Full PII (log user_id, not name + address + DOB together)
- High-frequency DEBUG noise left enabled in production

## SQLAlchemy Slow Query Logging

```python
# app/core/database.py
import logging
import time
from sqlalchemy import event

slow_query_logger = logging.getLogger("sqlalchemy.slow")
SLOW_QUERY_THRESHOLD_MS = 500

@event.listens_for(engine.sync_engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info["query_start"] = time.perf_counter()

@event.listens_for(engine.sync_engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    duration_ms = round((time.perf_counter() - conn.info["query_start"]) * 1000, 2)
    if duration_ms > SLOW_QUERY_THRESHOLD_MS:
        slow_query_logger.warning(
            "slow_query",
            extra={"duration_ms": duration_ms, "statement": statement[:500]},
        )
```

## Useful Log Schema for AI Debugging

Every log line should ideally contain:

```json
{
  "timestamp": "2026-04-06T14:32:01.123Z",
  "level": "error",
  "logger": "app.features.orders.service",
  "event": "order_creation_failed",
  "request_id": "a1b2c3d4-...",
  "user_id": "42",
  "item_count": 3,
  "reason": "db_integrity_error",
  "detail": "duplicate key value violates unique constraint ...",
  "exc_info": "Traceback (most recent call last): ..."
}
```

A log stream with this shape can be filtered, grouped, and summarized by an AI agent with a single query: *"show me all order_creation_failed events in the last 24 hours, grouped by reason."*
