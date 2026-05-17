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
