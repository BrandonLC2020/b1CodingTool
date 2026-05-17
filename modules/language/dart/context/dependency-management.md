# Dart: Dependency Management (Pub)

## pubspec.yaml
- **Environment:** Always pin the lower bound of the SDK: `sdk: ">=3.3.0 <4.0.0"`.
- **Dependencies:** Use `dependencies:` for runtime and `dev_dependencies:` for tools/tests.

## Versioning
- **Caret Syntax:** Use `^1.2.3` for semantic version compatibility.
- **Overrides:** Use `dependency_overrides:` sparingly for local path debugging.

## Commands
- `dart pub get`: Fetch dependencies.
- `dart pub upgrade`: Upgrade dependencies to latest within constraints.
- `dart pub outdated`: Check for updateable packages.

## Package Evaluation
Before adding a third-party dependency, evaluate it against:
- **Pub Points:** Prefer packages with 100+ points.
- **Popularity:** Look for high usage and active maintenance (commits in last 6 months).
- **Publisher:** Favor `dart.dev` or `flutter.dev` verified publishers.
- **License:** Ensure it uses a permissive license (e.g., MIT, BSD, Apache 2.0).
