# Design Spec: Swift Technology Module

**Date:** 2026-05-02
**Status:** Draft
**Topic:** Create a comprehensive b1 module for Swift development (SPM-focused, Xcode-agnostic).

## 1. Overview
The Swift Technology Module provides standardized guidelines, automation hooks, and agent skills for pure Swift development. It focuses on the Swift Package Manager (SPM) ecosystem and language-level best practices, remaining agnostic of IDE-specific files (like `.xcodeproj`) which are handled by the separate Xcode IDE module.

## 2. Architecture & File Structure

### 2.1 Module Metadata (`b1-module.yaml`)
```yaml
name: swift
version: 1.0.0
type: technology
description: "Core Swift language standards, SPM project structure, and safe concurrency guidelines."
skills:
  - id: swift-test-gen
    name: "Swift Test Generator"
    description: "Automated XCTest suite generation for Swift functions."
  - id: swift-concurrency-refactor
    name: "Concurrency Refactor"
    description: "Assist in transitioning completion-handlers to async/await."
hooks:
  post-install: "scripts/post-install.sh"
```

### 2.2 Directory Layout
```
modules/swift/
├── b1-module.yaml
├── context/
│   ├── best-practices.md
│   ├── conventions.md
│   ├── directory-structure.md
│   └── dependency-management.md
├── scripts/
│   └── post-install.sh
└── templates/
    └── XCTestTemplate.swift
```

## 3. Core Guidelines (Knowledge Base)

### 3.1 Conventions (`conventions.md`)
- **Naming:** `PascalCase` for types (structs, classes, enums), `camelCase` for variables, constants, and functions.
- **API Design:** Adherence to [Swift.org API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/). Focus on clarity at the point of use.
- **Formatting:** Use `swift-format` for consistent code styling.
- **Concurrency:** Prefer `async/await`, `Actors`, and `Tasks` over GCD and completion handlers.

### 3.2 Best Practices (`best-practices.md`)
- **Composition:** Favor Protocol-Oriented Programming (POP) and extensions over deep class inheritance.
- **Data Modeling:** Use `struct` and `enum` (value types) by default. Use `class` only when reference identity is required.
- **Error Handling:** Use `do-catch` blocks with custom `Error` enums for structured error handling.
- **Modern Swift:** Leverage opaque types (`some`), result builders, and generics where appropriate.

### 3.3 Directory Structure (`directory-structure.md`)
- **Standard SPM Layout:**
    - `Package.swift` at root.
    - `Sources/[TargetName]/` for source code.
    - `Tests/[TargetName]Tests/` for XCTest files.
- **Organization:** Keep targets small and focused.

### 3.4 Dependency Management (`dependency-management.md`)
- **SPM Focused:** Manage all dependencies via `Package.swift`.
- **Versioning:** Use semantic versioning requirements (e.g., `.upToNextMajor(from: "1.0.0")`).
- **Local Packages:** Use path-based dependencies for internal modularization during development.

## 4. Automation & Skills

### 4.1 Hooks
- **`post-install.sh`**: Runs `swift package resolve` to ensure dependencies are fetched immediately after module installation.

### 4.2 Agent Skills (Conceptual)
- **`swift-test-gen`**: Analyzes a Swift file and generates a corresponding `XCTest` file in the appropriate `Tests/` directory.
- **`swift-concurrency-refactor`**: Scans for completion-handler patterns and proposes `async` alternatives.

## 5. Success Criteria
1.  A valid `modules/swift/` directory exists with all specified files.
2.  `b1 install modules/swift` succeeds and registers the module.
3.  The `context/*.md` files correctly influence agent behavior in a Swift project.
4.  `post-install` hook successfully resolves dependencies in a test project.
