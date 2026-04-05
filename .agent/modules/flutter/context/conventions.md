# Flutter: Coding Conventions

## Dart Naming
- **Classes, enums, typedefs, extensions:** `PascalCase` — `UserProfile`, `AuthState`
- **Variables, parameters, named constructors, methods:** `camelCase` — `isLoading`, `fetchUser()`
- **Files and directories:** `snake_case` — `user_profile.dart`, `auth/`
- **Constants:** `camelCase` (Dart convention) — `const defaultTimeout = 30`
- **Private members:** prefix with `_` — `_controller`, `_handleTap()`

## File Organization
- One primary public class or widget per file.
- File name must match the primary class in snake_case: `class UserCard` → `user_card.dart`.
- Group related files in a feature directory, not by type (see directory-structure.md).

## Imports
Order imports in three groups separated by blank lines:
1. `dart:` SDK imports
2. `package:` external packages (flutter first, then others alphabetically)
3. Relative local imports

```dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/theme/app_theme.dart';
import 'user_card.dart';
```

## Widget Conventions
- Always pass `key` to the superclass constructor in stateful widgets and in any widget that appears in a list.
- Use `const` constructors wherever all fields are compile-time constants.
- Prefer named parameters over positional for any widget with more than one parameter.
- Declare `static const routeName = '/route'` inside page widgets for route references.

## Linting
- Enable `flutter_lints` (included in Flutter SDK) via `analysis_options.yaml`.
- Enable `avoid_print`, `prefer_const_constructors`, `use_key_in_widget_constructors`.
- Never suppress lints with `// ignore:` unless accompanied by a comment explaining why.

## Code Style
- Max line length: **80 characters** (default Dart formatter).
- Always run `dart format .` before committing.
- No trailing whitespace; no unnecessary blank lines inside methods.
- Use `??=`, `?.`, `??` and null-aware operators rather than null checks.
- Prefer `final` over `var` when a variable is never reassigned.
