# React Web: Logging Best Practices

## Philosophy

Good logs answer two questions without any additional context: **what happened**, and **why it matters**. In a React web app, logging spans two environments — the **browser** (client-side events, JS errors, user interactions) and the **server** (if using SSR/Next.js or a BFF). Both need structured, queryable output.

- **Structured over console strings.** `console.log("Login failed")` disappears after a page reload and can't be queried. Structured events sent to an observability platform (Sentry, Datadog, LogRocket) persist and can be analyzed at scale.
- **Correlation IDs.** Every user session and every significant action should carry a trace ID so that a sequence of events can be reconstructed in order.
- **Never log sensitive data.** The browser console is visible to anyone with DevTools open. Log pipelines often store data for 30–90 days. Treat client-side logs as public.

## Log Levels — When to Use Each

| Level | Use for |
|-------|---------|
| `debug` | Internal state during development. Strip from production builds. |
| `info` | Normal lifecycle events: page viewed, feature used, API call succeeded. |
| `warn` | Unexpected but non-fatal: deprecated prop used, retry triggered, feature flag defaulted. |
| `error` | Something broke: unhandled exception, API error, required resource missing. |

## A Thin Logger Wrapper

Wrap `console` in a lightweight logger so you can:
- Strip debug logs from production builds
- Attach consistent metadata (app version, session ID, timestamp) to every event
- Swap the transport later (e.g., send errors to Sentry) without changing call sites

```ts
// src/core/utils/logger.ts
type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEvent {
  event: string;
  level: LogLevel;
  timestamp: string;
  session_id: string;
  app_version: string;
  [key: string]: unknown;
}

const SESSION_ID = crypto.randomUUID();
const APP_VERSION = import.meta.env.VITE_APP_VERSION ?? 'unknown';
const IS_PROD = import.meta.env.PROD;

function emit(level: LogLevel, event: string, context: Record<string, unknown> = {}) {
  const entry: LogEvent = {
    event,
    level,
    timestamp: new Date().toISOString(),
    session_id: SESSION_ID,
    app_version: APP_VERSION,
    ...context,
  };

  if (level === 'debug' && IS_PROD) return;  // strip debug in prod

  console[level](IS_PROD ? JSON.stringify(entry) : entry);

  if (level === 'error') {
    // forward to error tracking
    reportToSentry(entry);
  }
}

export const logger = {
  debug: (event: string, ctx?: Record<string, unknown>) => emit('debug', event, ctx),
  info:  (event: string, ctx?: Record<string, unknown>) => emit('info',  event, ctx),
  warn:  (event: string, ctx?: Record<string, unknown>) => emit('warn',  event, ctx),
  error: (event: string, ctx?: Record<string, unknown>) => emit('error', event, ctx),
};
```

## Error Tracking: Sentry

Use Sentry for unhandled JS errors and React rendering errors. It captures stack traces, breadcrumbs, and device context automatically.

```bash
npm install @sentry/react
```

```ts
// src/main.tsx
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  release: import.meta.env.VITE_APP_VERSION,
  tracesSampleRate: 0.1,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({ maskAllText: true, blockAllMedia: true }),
  ],
});
```

## Error Boundaries with Logging

Wrap route-level subtrees in error boundaries that log to Sentry before rendering a fallback:

```tsx
// src/core/components/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';
import * as Sentry from '@sentry/react';
import { logger } from '@/core/utils/logger';

interface Props { children: ReactNode; fallback?: ReactNode; context?: string; }
interface State { hasError: boolean; }

export class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };

  componentDidCatch(error: Error, info: ErrorInfo) {
    logger.error('react_render_error', {
      context: this.props.context ?? 'unknown',
      error: error.message,
      component_stack: info.componentStack ?? undefined,
    });
    Sentry.captureException(error, { extra: { componentStack: info.componentStack } });
  }

  static getDerivedStateFromError() { return { hasError: true }; }

  render() {
    return this.state.hasError
      ? (this.props.fallback ?? <p>Something went wrong.</p>)
      : this.props.children;
  }
}
```

## Navigation Logging

Log every route change so you can reconstruct the user journey before an error:

```ts
// src/core/router/router.tsx (React Router)
router.subscribe((state) => {
  logger.info('page_viewed', {
    path: state.location.pathname,
    search: state.location.search,
  });
  Sentry.addBreadcrumb({
    category: 'navigation',
    message: state.location.pathname,
    level: 'info',
  });
});
```

## API Call Logging

Wrap `fetch` (or your HTTP client) to log every request and response:

```ts
// src/core/services/httpClient.ts
export async function httpClient(url: string, init?: RequestInit): Promise<Response> {
  const method = init?.method ?? 'GET';
  logger.debug('http_request', { method, url });

  const start = performance.now();
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch (err) {
    logger.error('http_network_error', { method, url, error: String(err) });
    throw err;
  }

  const duration_ms = Math.round(performance.now() - start);
  const level = response.ok ? 'info' : 'warn';
  logger[level]('http_response', { method, url, status: response.status, duration_ms });

  if (response.status >= 500) {
    logger.error('http_server_error', { method, url, status: response.status });
  }
  return response;
}
```

## Structured Log Events — Examples

```ts
// Authentication
logger.info('user_login_succeeded', { user_id: user.id });
logger.warn('user_login_failed', { reason: 'invalid_credentials', email_domain: 'example.com' });

// Feature usage
logger.info('feature_used', { feature: 'export_csv', row_count: 1200 });

// Errors
logger.error('payment_failed', { order_id: order.id, reason: result.error_code });
```

## What to Log (and When)

- **Page views:** every route change (path, query params — not query values containing IDs/tokens)
- **Auth events:** login success/failure (reason only, never credential), logout, session expired
- **API calls:** every request (method, URL) and response (status, duration) — response body only at debug
- **User actions:** significant interactions (form submitted, purchase attempted, filter applied)
- **Errors:** every caught exception before it's suppressed, every Error Boundary catch
- **Feature flags:** which flags are active at session start (useful for debugging flag-specific bugs)

## What NOT to Log

- Passwords, tokens, API keys — ever
- Full names, email addresses, phone numbers in log payloads (log user_id instead)
- Raw form field values (may contain passwords or card numbers)
- Query string values that may contain auth tokens (`?token=...`)
- Debug-level logs in production builds

## SSR / Next.js: Server-Side Logs

For Next.js apps, server-side logs (API routes, Server Components, middleware) should use a Node.js-compatible structured logger like `pino`:

```ts
// lib/logger.ts (server-side only)
import pino from 'pino';

export const serverLogger = pino({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  ...(process.env.NODE_ENV !== 'production' && {
    transport: { target: 'pino-pretty' },
  }),
});
```

Attach a `request_id` in middleware and forward it via response headers so client-side logs can be correlated with server logs:

```ts
// middleware.ts
export function middleware(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const response = NextResponse.next();
  response.headers.set('x-request-id', requestId);
  return response;
}
```
