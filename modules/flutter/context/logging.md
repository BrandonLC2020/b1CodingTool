# Flutter: Logging Best Practices

## Philosophy

Good logs answer two questions without any additional context: **what happened**, and **why it matters**. In Flutter, logs serve three distinct audiences: the developer at a terminal, a crash reporting dashboard, and an AI agent analyzing a production incident.

- **Structured over print statements.** `print("Login failed")` is invisible in production and unsearchable. A structured log event with level, context, and metadata is actionable.
- **Strip sensitive data before production.** Debug logs in development may be verbose; production logs must never contain tokens, passwords, or raw PII.
- **Crash context is everything.** The most valuable logs in mobile are the breadcrumbs recorded *before* a crash — they reconstruct the user journey without needing a repro.

## Log Levels — When to Use Each

| Level | Use for |
|-------|---------|
| `verbose` / `trace` | Low-level state dumps, widget lifecycle events. Development only. |
| `debug` | Data flows, provider state changes, API response bodies. Development only. |
| `info` | Normal lifecycle events: screen viewed, user action completed, API call succeeded. |
| `warning` | Unexpected but recoverable: retry triggered, feature flag defaulted, optional permission denied. |
| `error` | A specific operation failed: API returned error, local DB write failed, required resource missing. |
| `wtf` (fatal) | Unrecoverable: app cannot continue, invariant violated. |

## Setup: the `logger` Package

```yaml
# pubspec.yaml
dependencies:
  logger: ^2.0.0
```

Define a singleton logger at app level:

```dart
// lib/core/logging/app_logger.dart
import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';

final appLogger = Logger(
  level: kDebugMode ? Level.debug : Level.info,
  printer: kDebugMode
      ? PrettyPrinter(methodCount: 3, printTime: true)
      : ProductionPrinter(),          // see below
  filter: ProductionFilter(),         // only logs at >= level
);

/// JSON printer for production — structured and machine-readable.
class ProductionPrinter extends LogPrinter {
  @override
  List<String> log(LogEvent event) {
    final error = event.error;
    return [
      {
        'level': event.level.name,
        'message': event.message,
        'timestamp': DateTime.now().toUtc().toIso8601String(),
        if (error != null) 'error': error.toString(),
        if (event.stackTrace != null) 'stack_trace': event.stackTrace.toString(),
      }.toString(),
    ];
  }
}
```

## Structured Logging Pattern

Never log raw strings. Pass a structured map as the message so log aggregators and AI agents can parse it:

```dart
// Good
appLogger.i({
  'event': 'payment_initiated',
  'order_id': order.id,
  'amount': order.total,
  'currency': order.currency,
});

// Bad
appLogger.i('Payment initiated for order ${order.id}');
```

## Crash Reporting: Sentry

Use `sentry_flutter` for production crash reporting. Sentry captures unhandled exceptions, attaches breadcrumbs, and stores them in a searchable dashboard.

```yaml
dependencies:
  sentry_flutter: ^8.0.0
```

```dart
// lib/main.dart
import 'package:sentry_flutter/sentry_flutter.dart';

Future<void> main() async {
  await SentryFlutter.init(
    (options) {
      options.dsn = const String.fromEnvironment('SENTRY_DSN');
      options.environment = const String.fromEnvironment('ENV', defaultValue: 'development');
      options.tracesSampleRate = 0.2;      // 20% of sessions traced for performance
      options.attachScreenshot = true;     // capture screenshot on crash
    },
    appRunner: () => runApp(const App()),
  );
}
```

## Bloc Observer: Log Every State Transition

Register a global `BlocObserver` to log every event, state change, transition, and error across all Blocs and Cubits. This is the single highest-value logging addition for flutter_bloc apps.

```dart
// lib/core/logging/app_bloc_observer.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'app_logger.dart';

class AppBlocObserver extends BlocObserver {
  @override
  void onCreate(BlocBase bloc) {
    super.onCreate(bloc);
    appLogger.d({'event': 'bloc_created', 'bloc': bloc.runtimeType.toString()});
  }

  @override
  void onEvent(Bloc bloc, Object? event) {
    super.onEvent(bloc, event);
    appLogger.d({'event': 'bloc_event', 'bloc': bloc.runtimeType.toString(), 'event_type': event.runtimeType.toString()});
  }

  @override
  void onChange(BlocBase bloc, Change change) {
    super.onChange(bloc, change);
    appLogger.i({
      'event': 'bloc_state_changed',
      'bloc': bloc.runtimeType.toString(),
      'from': change.currentState.runtimeType.toString(),
      'to': change.nextState.runtimeType.toString(),
    });
  }

  @override
  void onError(BlocBase bloc, Object error, StackTrace stackTrace) {
    appLogger.e(
      {'event': 'bloc_error', 'bloc': bloc.runtimeType.toString()},
      error: error,
      stackTrace: stackTrace,
    );
    super.onError(bloc, error, stackTrace);
  }

  @override
  void onClose(BlocBase bloc) {
    super.onClose(bloc);
    appLogger.d({'event': 'bloc_closed', 'bloc': bloc.runtimeType.toString()});
  }
}
```

Register in `main.dart`:
```dart
void main() {
  Bloc.observer = AppBlocObserver();
  runApp(const App());
}
```

## Navigation Logging

Log every route change to reconstruct the user journey before a crash:

```dart
// lib/core/router/router.dart (go_router)
final router = GoRouter(
  observers: [AppRouteObserver()],
  routes: [...],
);

class AppRouteObserver extends NavigatorObserver {
  @override
  void didPush(Route route, Route? previousRoute) {
    appLogger.i({'event': 'screen_pushed', 'screen': route.settings.name});
    Sentry.addBreadcrumb(Breadcrumb.navigation(
      from: previousRoute?.settings.name,
      to: route.settings.name,
    ));
  }

  @override
  void didPop(Route route, Route? previousRoute) {
    appLogger.i({'event': 'screen_popped', 'screen': route.settings.name});
  }
}
```

## Network Request Logging

Use a `Dio` interceptor (or equivalent) to log every outbound request and response:

```dart
class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    appLogger.d({
      'event': 'http_request',
      'method': options.method,
      'url': options.uri.toString(),
    });
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    appLogger.i({
      'event': 'http_response',
      'method': response.requestOptions.method,
      'url': response.requestOptions.uri.toString(),
      'status_code': response.statusCode,
    });
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    appLogger.e({
      'event': 'http_error',
      'method': err.requestOptions.method,
      'url': err.requestOptions.uri.toString(),
      'status_code': err.response?.statusCode,
      'error': err.message,
    }, error: err, stackTrace: err.stackTrace);
    handler.next(err);
  }
}
```

## What to Log (and When)

- **App lifecycle:** cold start, resume from background, push notification received
- **Authentication:** login success/failure (with reason, never the credential), token refresh, logout
- **Navigation:** every screen push/pop (breadcrumb for crash context)
- **API calls:** every request (method, URL) and response (status code) — response body only at DEBUG
- **Bloc transitions:** every state change via `AppBlocObserver`
- **Errors:** every caught exception — log it before rethrowing or recovering
- **User actions:** significant interactions (form submitted, purchase attempted, permission granted/denied)

## What NOT to Log

- Passwords, tokens, API keys — ever
- Biometric or health data
- Full response bodies containing PII
- Debug-level logs in production builds (use `kDebugMode` / `ProductionFilter`)

## Development: Flipper Integration

In development, use `flipper_plugin_log` to view structured logs in the Flipper desktop tool without polluting the terminal:

```yaml
dev_dependencies:
  flipper_plugin_log: ^0.1.0
```

This gives you a filterable, searchable log viewer during development with no production overhead.
