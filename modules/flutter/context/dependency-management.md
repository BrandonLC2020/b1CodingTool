# Flutter: Dependency Management with pub

## Overview

Flutter uses **pub** — Dart's built-in package manager — exclusively. There is no alternative; all Flutter and Dart packages are distributed through [pub.dev](https://pub.dev). The `flutter pub` command wraps `dart pub` with Flutter-specific additions.

## pubspec.yaml

`pubspec.yaml` is the project manifest. It declares dependencies, dev dependencies, assets, and Flutter-specific config.

```yaml
name: my_app
description: A Flutter application.
version: 1.0.0+1          # semver+build_number (used for app store versioning)

environment:
  sdk: ">=3.3.0 <4.0.0"  # Dart SDK constraint — always pin the lower bound

dependencies:
  flutter:
    sdk: flutter
  flutter_bloc: ^8.1.6
  go_router: ^14.0.0
  sentry_flutter: ^8.0.0
  dio: ^5.4.0
  logger: ^2.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
  bloc_test: ^9.1.7
  mocktail: ^1.0.4
  build_runner: ^2.4.9    # required for code generation (json_serializable, freezed, etc.)

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/fonts/
```

## Version Constraints

Pub uses semantic versioning. Choose the right constraint for each dependency:

| Constraint | Meaning | Use when |
|------------|---------|----------|
| `^1.2.3` | `>=1.2.3 <2.0.0` | Most dependencies — allows patch and minor updates |
| `>=1.0.0 <2.0.0` | Explicit range | When `^` doesn't express the range you need |
| `1.2.3` | Exact pin | Rarely — only when a specific version is required |
| `any` | No constraint | Never in production code |

**Prefer `^` (caret) constraints.** They allow non-breaking updates while preventing major version jumps that may contain breaking changes.

## pubspec.lock

`pubspec.lock` records the exact resolved version of every dependency (direct and transitive). Always commit it to version control for apps. For publishable packages, do not commit it (pub.dev ignores it).

```bash
# pubspec.lock should be in .gitignore for packages, committed for apps
```

## Common Commands

```bash
flutter pub get               # Install dependencies from pubspec.yaml (updates lock if needed)
flutter pub upgrade           # Upgrade all dependencies to latest allowed by constraints
flutter pub upgrade --major-versions  # Upgrade constraints in pubspec.yaml to latest major
flutter pub outdated          # Show which packages have newer versions available
flutter pub add dio           # Add a dependency and run pub get
flutter pub add --dev mocktail  # Add a dev dependency
flutter pub remove dio        # Remove a dependency
flutter pub run build_runner build  # Run code generation (one-shot)
flutter pub run build_runner watch  # Run code generation (watch mode during development)
dart pub publish              # Publish a package to pub.dev
```

## Code Generation

Many popular Flutter packages (Freezed, json_serializable, injectable, auto_route) use `build_runner` to generate `.g.dart` or `.freezed.dart` files. These generated files should be **committed to version control** — they are part of your app's source, not build artifacts.

```bash
# One-shot generation (CI, after pulling changes)
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode during development
flutter pub run build_runner watch --delete-conflicting-outputs
```

Add to your `.gitignore` only if you choose not to commit generated files (not recommended — it breaks `flutter pub get` for new contributors without an extra step):
```
# Only add these if you explicitly choose not to commit generated files
# *.g.dart
# *.freezed.dart
```

## Resolving Dependency Conflicts

Pub resolves a single consistent set of package versions across all dependencies. If two packages require incompatible versions of a third package, pub will report a conflict.

**Resolution strategies:**

1. **Run `flutter pub upgrade`** — often a newer version of one of the conflicting packages has relaxed its constraint.
2. **Check pub.dev** — look at each conflicting package's changelog to understand what version is needed.
3. **Use `dependency_overrides`** — a last resort that forces a specific version regardless of constraints. Document why and plan to remove it.

```yaml
# pubspec.yaml — last resort only, always document
dependency_overrides:
  some_package: 2.3.1   # pinned because package_foo hasn't updated yet — see issue #123
```

## Checking Package Quality on pub.dev

Before adding a dependency, check its pub.dev score:

- **Pub points** — automated quality score (documentation, static analysis, platform support)
- **Likes** — community endorsement
- **Popularity** — usage across pub.dev packages
- **Publisher verification** — `dart.dev` and `flutter.dev` verified publishers are first-party packages

Prefer packages maintained by `flutter.dev`/`dart.dev` or well-maintained community packages with high pub points. Avoid packages with no activity in 12+ months for critical functionality.

## Dependency Types

| Type | Declared under | Included in release build |
|------|---------------|--------------------------|
| Regular | `dependencies:` | Yes |
| Dev | `dev_dependencies:` | No (tests, code gen tools only) |
| SDK | `sdk: flutter` | Bundled with Flutter SDK |

Keep `dev_dependencies` clean — `build_runner`, test utilities, and linting tools belong there, never in `dependencies`.
