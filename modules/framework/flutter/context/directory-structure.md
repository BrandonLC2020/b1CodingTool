# Flutter: Directory Structure

## Feature-First Layout (Recommended)
Organize code by **feature**, not by technical layer. Each feature is a self-contained directory.

```
lib/
├── main.dart                  # Entry point — ProviderScope + runApp only
├── app.dart                   # MaterialApp / GoRouter setup
├── core/                      # Shared, app-wide code
│   ├── constants/
│   │   └── app_constants.dart
│   ├── theme/
│   │   ├── app_theme.dart
│   │   └── app_colors.dart
│   ├── utils/
│   │   └── date_utils.dart
│   ├── widgets/               # Truly shared UI components
│   │   ├── loading_indicator.dart
│   │   └── error_view.dart
│   └── router/
│       └── router.dart        # GoRouter definition
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── models/        # Serializable data classes (JSON ↔ Dart)
│   │   │   │   └── user_model.dart
│   │   │   ├── data_sources/  # Remote (API) and local (cache) sources
│   │   │   │   ├── auth_remote_data_source.dart
│   │   │   │   └── auth_local_data_source.dart
│   │   │   └── repositories/  # Concrete repository implementations
│   │   │       └── auth_repository_impl.dart
│   │   ├── domain/
│   │   │   ├── entities/      # Pure Dart business objects (no JSON)
│   │   │   │   └── user.dart
│   │   │   ├── repositories/  # Abstract repository interfaces
│   │   │   │   └── auth_repository.dart
│   │   │   └── usecases/      # Single-responsibility business actions
│   │   │       └── sign_in_usecase.dart
│   │   └── presentation/
│   │       ├── pages/         # Full screens, one file per route
│   │       │   ├── login_page.dart
│   │       │   └── register_page.dart
│   │       ├── widgets/       # Feature-local widgets not shared elsewhere
│   │       │   └── login_form.dart
│   │       └── providers/     # Riverpod providers for this feature
│   │           └── auth_providers.dart
│   └── profile/
│       └── ...                # Same structure as auth/
test/
├── unit/
│   └── features/
│       └── auth/
│           └── auth_notifier_test.dart
├── widget/
│   └── features/
│       └── auth/
│           └── login_page_test.dart
└── golden/
    └── login_page_golden_test.dart
```

## File Naming Rules
| Type | Convention | Example |
|------|-----------|---------|
| Widgets / Pages | `snake_case.dart` | `user_profile_page.dart` |
| Providers | `<feature>_providers.dart` | `auth_providers.dart` |
| Models (data layer) | `<name>_model.dart` | `user_model.dart` |
| Entities (domain layer) | `<name>.dart` (no suffix) | `user.dart` |
| Repositories (abstract) | `<name>_repository.dart` | `auth_repository.dart` |
| Repositories (impl) | `<name>_repository_impl.dart` | `auth_repository_impl.dart` |
| Tests | `<file_under_test>_test.dart` | `auth_notifier_test.dart` |

## Key Files at Project Root
| File | Purpose |
|------|---------|
| `pubspec.yaml` | Dependencies and assets |
| `analysis_options.yaml` | Linting rules |
| `l10n.yaml` | Localization config (if using `flutter_localizations`) |
| `.env` / `dart_defines/` | Environment-specific config (never commit secrets) |
