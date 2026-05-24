# Design Spec: Dart Language Module

**Date:** 2026-05-17
**Status:** Approved
**Topic:** Implementation of the Dart language module for the b1CodingTool ecosystem.

## 1. Overview
The Dart Language Module provides a foundational layer for Dart development within the b1Coding ecosystem. It establishes language-level standards, automated skills, and core CLI enhancements to ensure agents can intelligently parse, translate, and interact with Dart code. This module serves as the base for framework-specific modules like Flutter.

## 2. Architecture & File Structure

### 2.1 Module Metadata (`b1-module.yaml`)
```yaml
name: dart
version: 1.0.0
type: development
description: "Core Dart language standards, sound null-safety, and modern pub ecosystem guidelines."
skills:
  - name: "Dart Test Generator"
    description: "Automated generation of package:test suites for Dart classes and functions."
  - name: "Pub Dependency Manager"
    description: "Assists in adding, removing, and upgrading dependencies via pub.dev."
  - name: "Sealed Class Refactor"
    description: "Refactor class hierarchies to use Dart 3+ sealed classes for exhaustive switching."
hooks:
  post-install: "scripts/post-install.sh"
```

### 2.2 Directory Layout
```text
modules/language/dart/
├── b1-module.yaml
├── context/
│   ├── conventions.md          # Naming, linting, and style
│   ├── modern-dart.md          # Dart 3+ features (Records, Patterns, Sealed)
│   ├── dependency-management.md # Pub ecosystem and pubspec.yaml
│   └── testing.md              # package:test and async verification
├── scripts/
│   └── post-install.sh         # Dependency resolution logic
└── templates/                  # (Future expansion: CLI/Library templates)
```

## 3. Core CLI Enhancements (Python Engine)

### 3.1 Rule Extraction (`src/b1/core/rule_extractor.py`)
- **Native Marker Support:** Extend regex to support Dart-style comments:
  - `// b1:generalized:start`
  - `// b1:generalized:end`
- **Docstring Harvesting:** Recognition of `/// @b1-learning` patterns in triple-slash documentation.

### 3.2 Agent Translation (`src/b1/core/translator.py`)
- **Syntax Awareness:** Map `.dart` extensions to `dart` syntax highlighting in all generated agent files (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`).
- **Claude-Specific Formatting:** Wrap Dart context in `<dart_context>` tags for improved agent focus.

## 4. Knowledge Base Content

### 4.1 Conventions (`conventions.md`)
- **Naming:** `camelCase` (variables/functions), `PascalCase` (types), `snake_case` (files).
- **Formatting:** Enforce `dart format` (80 char limit).
- **Lints:** Standardize on `package:lints/recommended.yaml`.

### 4.2 Modern Dart (`modern-dart.md`)
- **Dart 3+ Features:** Focus on sealed classes, records, and pattern matching.
- **Null Safety:** Strict rules for sound null safety.

### 4.3 Dependency Management (`dependency-management.md`)
- **Pub.dev:** Evaluation criteria for community packages.
- **Versioning:** Semver constraints and dependency overrides.

### 4.4 Testing (`testing.md`)
- **Package:test:** standard test directory layout and async testing patterns.
- **Mocks:** Preference for `mocktail` or fakes.

## 5. Automation
- **`post-install.sh`**: Detects `pubspec.yaml` and executes `dart pub get` (or `flutter pub get`) to ensure an immediately usable environment.

## 6. Success Criteria
1. `modules/language/dart/` exists with valid manifest and context files.
2. `src/b1/core/rule_extractor.py` successfully extracts rules from `.dart` files.
3. `b1 pair` generates `.dart`-aware configuration files.
4. `b1 install dart` successfully triggers `post-install` dependency resolution.
