# Django: Logging Best Practices

## Philosophy

Good logs answer two questions without any additional context: **what happened**, and **why it matters**. Every log line should be self-contained enough that a human or AI agent reading it in isolation — with no knowledge of the codebase — can understand the event and act on it.

- **Structured over narrative.** Key-value pairs beat prose. `{"event": "user_login_failed", "email": "a@b.com", "reason": "bad_password", "attempt": 3}` is queryable; `"Login failed for a@b.com"` is not.
- **Correlation IDs everywhere.** Every request gets a UUID. Every log line for that request carries it. This is the thread that lets you reconstruct a full request trace from fragmented log lines.
- **Levels mean something.** Don't log everything at INFO. Use levels consistently so alert thresholds are meaningful.

## Log Levels — When to Use Each

| Level | Use for |
|-------|---------|
| `DEBUG` | Internal state, SQL queries, variable values during development. Never enabled in production by default. |
| `INFO` | Normal lifecycle events: request received, user authenticated, background job started/completed. |
| `WARNING` | Unexpected but recoverable situations: deprecated API used, retry attempt, config fallback triggered. |
| `ERROR` | A specific operation failed and requires investigation: payment failed, external API returned 5xx, DB write failed. |
| `CRITICAL` | The application cannot continue operating: DB unreachable, missing required config, unrecoverable startup failure. |

## Setup: structlog + Django logging

Use `structlog` for structured logging. It integrates with Python's standard `logging` module so Django's built-in log calls are also captured.

```bash
uv add structlog
```

```python
# config/settings/base.py
import structlog

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),  # human-friendly in dev
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console" if DEBUG else "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"level": "INFO"},
        "django.db.backends": {"level": "DEBUG" if DEBUG else "WARNING"},  # SQL in dev only
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,          # injects request-scoped context
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

## Correlation IDs via Middleware

Assign a unique `request_id` to every request and bind it into the structlog context so all subsequent log calls automatically include it.

```python
# apps/core/middleware.py
import uuid
import structlog
from structlog.contextvars import clear_contextvars, bind_contextvars

logger = structlog.get_logger()

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        clear_contextvars()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.path,
        )

        logger.info("request_started")
        response = self.get_response(request)

        bind_contextvars(status_code=response.status_code)
        logger.info("request_finished")
        return response
```

Register in settings:
```python
MIDDLEWARE = [
    "apps.core.middleware.RequestLoggingMiddleware",
    # ... other middleware
]
```

## Logging in Application Code

Get a module-level logger and use bound loggers to attach context:

```python
import structlog

logger = structlog.get_logger(__name__)

def process_payment(order: Order, payment_method: PaymentMethod) -> PaymentResult:
    log = logger.bind(order_id=str(order.id), user_id=str(order.user_id), amount=order.total)
    log.info("payment_initiated")

    try:
        result = payment_gateway.charge(payment_method, order.total)
    except PaymentGatewayError as e:
        log.error("payment_gateway_error", error=str(e), gateway=e.gateway_name)
        raise

    if not result.success:
        log.warning("payment_declined", reason=result.decline_reason, code=result.code)
        return result

    log.info("payment_succeeded", transaction_id=result.transaction_id)
    return result
```

## What to Log (and When)

**Request lifecycle:**
- Request received (method, path, user_id if authenticated)
- Request completed (status code, duration_ms)
- Unhandled exceptions (full traceback, request context)

**Business events:**
- User authentication (success and failure — with failure reason, never the password)
- State transitions on important models (`order.status` changed from `pending` → `paid`)
- Background job start, completion, and failure

**External calls:**
- Every outbound HTTP request (method, URL, status_code, duration_ms)
- DB query slow log (queries exceeding a threshold — enable `django.db.backends` at DEBUG)
- Cache hit/miss for expensive operations

**Errors:**
- Every caught exception that's suppressed — log it at WARNING/ERROR, never silently discard
- Every `except Exception` block must log the exception

## What NOT to Log

- Passwords, tokens, API keys, secrets — ever
- Full credit card numbers, SSNs, government IDs
- Raw request bodies that may contain any of the above
- PII beyond what's necessary for debugging (email is usually sufficient; full address is not)
- High-cardinality noise at INFO level (e.g., every cache lookup in a hot path)

## Celery Task Logging

Bind task context at the start of every task:

```python
import structlog
from celery import shared_task

logger = structlog.get_logger(__name__)

@shared_task(bind=True)
def send_welcome_email(self, user_id: int) -> None:
    log = logger.bind(task_id=self.request.id, task="send_welcome_email", user_id=user_id)
    log.info("task_started")
    try:
        user = User.objects.get(pk=user_id)
        email_service.send_welcome(user)
        log.info("task_succeeded")
    except User.DoesNotExist:
        log.error("task_failed", reason="user_not_found")
        raise
    except Exception as e:
        log.error("task_failed", reason=str(e), exc_info=True)
        raise self.retry(exc=e, countdown=60)
```

## Useful Log Schema for AI Debugging

Every log line should ideally contain:

```json
{
  "timestamp": "2026-04-06T14:32:01.123Z",
  "level": "error",
  "logger": "apps.payments.service",
  "event": "payment_gateway_error",
  "request_id": "a1b2c3d4-...",
  "user_id": "42",
  "order_id": "ord_789",
  "amount": 59.99,
  "gateway": "stripe",
  "error": "connection timeout after 5000ms",
  "exc_info": "Traceback (most recent call last): ..."
}
```

A log stream with this shape can be filtered, grouped, and summarized by an AI agent with a single query: *"show me all payment_gateway_error events in the last hour, grouped by gateway and error type."*
