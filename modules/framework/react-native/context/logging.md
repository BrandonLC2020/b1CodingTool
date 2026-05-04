# React Native (Expo): Logging Best Practices

## Philosophy

Good logs answer two questions without any additional context: **what happened**, and **why it matters**. In React Native, logs serve three distinct audiences: the developer in Expo DevTools, a crash reporting dashboard, and an AI agent analyzing a production incident.

- **Structured over `console.log`.** `console.log("Payment failed")` is invisible in production. Structured events sent to Sentry (or similar) persist across sessions and can be queried at scale.
- **Breadcrumbs before crashes.** The most valuable logs in mobile are the events recorded *before* a crash. They reconstruct the user journey without needing a repro.
- **Strip sensitive data.** Device logs can be extracted from bug reports. Production logs may be stored for months. Never log tokens, passwords, or raw PII.

## Log Levels — When to Use Each

| Level | Use for |
|-------|---------|
| `debug` | Internal state, hook values, API response bodies. Development only. |
| `info` | Normal lifecycle: screen viewed, user action completed, API call succeeded. |
| `warn` | Unexpected but recoverable: retry triggered, permission denied, feature flag defaulted. |
| `error` | Something broke: unhandled exception, API error, required native module unavailable. |

## A Thin Logger Wrapper

Wrap logging in a single module so you can strip debug output from production builds and attach consistent context to every event:

```ts
// src/core/utils/logger.ts
import * as Sentry from '@sentry/react-native';
import { Platform } from 'react-native';

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const IS_DEV = __DEV__;

function emit(level: LogLevel, event: string, context: Record<string, unknown> = {}) {
  const entry = {
    event,
    level,
    timestamp: new Date().toISOString(),
    platform: Platform.OS,
    ...context,
  };

  if (level === 'debug' && !IS_DEV) return;   // strip debug in production

  if (IS_DEV) {
    console[level](`[${level.toUpperCase()}] ${event}`, context);
  }

  // Add as Sentry breadcrumb for crash context
  Sentry.addBreadcrumb({
    category: event,
    data: context,
    level: level === 'warn' ? 'warning' : level,
  });

  if (level === 'error') {
    Sentry.captureMessage(event, { level: 'error', extra: context });
  }
}

export const logger = {
  debug: (event: string, ctx?: Record<string, unknown>) => emit('debug', event, ctx),
  info:  (event: string, ctx?: Record<string, unknown>) => emit('info',  event, ctx),
  warn:  (event: string, ctx?: Record<string, unknown>) => emit('warn',  event, ctx),
  error: (event: string, ctx?: Record<string, unknown>) => emit('error', event, ctx),
  exception: (event: string, error: unknown, ctx?: Record<string, unknown>) => {
    emit('error', event, { ...ctx, error: String(error) });
    Sentry.captureException(error, { extra: ctx });
  },
};
```

## Crash Reporting: Sentry

Use `@sentry/react-native` for unhandled JS and native crashes. It wraps the app at the root level, captures native stack traces, and stores breadcrumbs leading up to a crash.

```bash
npx expo install @sentry/react-native
```

```ts
// app/_layout.tsx
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
  environment: process.env.EXPO_PUBLIC_ENV ?? 'development',
  tracesSampleRate: 0.1,
  enableNativeNagger: false,     // suppress dev warnings about native setup
});

export default Sentry.wrap(RootLayout);
```

Upload source maps as part of your EAS build to get readable stack traces in the Sentry dashboard. Configure this in `app.json`:

```json
{
  "expo": {
    "plugins": [["@sentry/react-native/expo", { "organization": "...", "project": "..." }]]
  }
}
```

## Navigation Logging (Expo Router)

Log every screen visit and add navigation breadcrumbs. Use Expo Router's `usePathname` hook to track the current route:

```tsx
// src/core/components/NavigationLogger.tsx
import { useEffect } from 'react';
import { usePathname } from 'expo-router';
import * as Sentry from '@sentry/react-native';
import { logger } from '@/core/utils/logger';

export function NavigationLogger() {
  const pathname = usePathname();

  useEffect(() => {
    logger.info('screen_viewed', { screen: pathname });
    Sentry.addBreadcrumb({ category: 'navigation', message: pathname, level: 'info' });
  }, [pathname]);

  return null;
}
```

Mount it inside the root layout:
```tsx
// app/_layout.tsx
export default function RootLayout() {
  return (
    <>
      <NavigationLogger />
      <Slot />
    </>
  );
}
```

## Network Request Logging

Log every outbound API call. Use an Axios or `fetch` wrapper interceptor:

```ts
// src/core/services/httpClient.ts
export async function httpClient(url: string, init?: RequestInit): Promise<Response> {
  const method = init?.method ?? 'GET';
  logger.debug('http_request', { method, url });

  const start = Date.now();
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch (err) {
    logger.exception('http_network_error', err, { method, url });
    throw err;
  }

  const duration_ms = Date.now() - start;
  const level = response.ok ? 'info' : 'warn';
  logger[level]('http_response', { method, url, status: response.status, duration_ms });

  if (response.status >= 500) {
    logger.error('http_server_error', { method, url, status: response.status });
  }
  return response;
}
```

## App Lifecycle Logging

Log app state transitions (foreground, background, inactive) to understand context around crashes:

```ts
// src/core/hooks/useAppLifecycleLogger.ts
import { useEffect } from 'react';
import { AppState } from 'react-native';
import { logger } from '@/core/utils/logger';

export function useAppLifecycleLogger() {
  useEffect(() => {
    const sub = AppState.addEventListener('change', (nextState) => {
      logger.info('app_state_changed', { state: nextState });
    });
    return () => sub.remove();
  }, []);
}
```

Mount in the root layout.

## Structured Log Events — Examples

```ts
// Authentication
logger.info('user_login_succeeded', { user_id: user.id });
logger.warn('user_login_failed', { reason: 'bad_credentials' });

// Permissions
logger.info('permission_requested', { permission: 'camera', granted: true });
logger.warn('permission_denied', { permission: 'notifications' });

// Business events
logger.info('purchase_completed', { product_id: item.id, price: item.price });
logger.error('purchase_failed', { product_id: item.id, reason: error.code });

// Push notifications
logger.info('push_notification_received', { type: notification.type });
```

## What to Log (and When)

- **App lifecycle:** cold start, foreground/background transitions, crash recovery
- **Screen views:** every route change (breadcrumb for crash context)
- **Auth events:** login success/failure (reason, never the credential), logout, session expired, token refreshed
- **API calls:** every request (method, URL) and response (status, duration_ms)
- **Permissions:** every request and result (granted/denied)
- **Errors:** every caught exception — log before rethrowing or recovering
- **Push notifications:** received, tapped, dismissed
- **Deep links:** every deep link handled (URL scheme, source)

## What NOT to Log

- Passwords, tokens, API keys — ever
- Full names, emails, or phone numbers in log payloads (log user_id instead)
- Location data beyond coarse region (city at most)
- Raw push notification payloads that may contain sensitive content
- Debug-level logs in production builds (`__DEV__` guard)

## Development: Expo DevTools + Flipper

In development, logs appear in the Expo terminal and in Flipper (if installed). Use the `react-native-logs` library if you want log level filtering and color coding in the terminal:

```bash
npx expo install react-native-logs
```

This gives you filterable, colored log output during development with no production overhead.
