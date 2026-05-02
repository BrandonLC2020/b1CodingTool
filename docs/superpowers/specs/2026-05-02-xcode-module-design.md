# Design Spec: Xcode IDE Module (Tuist-Native)

**Date:** 2026-05-02
**Status:** Draft
**Topic:** Create a comprehensive b1 module for Xcode IDE management using Tuist.

## 1. Overview
The Xcode IDE Module provides standardized guidelines, automation hooks, and agent skills for managing Xcode projects as code via [Tuist](https://tuist.io). It ensures perfect parity between physical folders and Xcode groups, prevents project file merge conflicts, and enables AI agents to reliably modify project structures by editing Swift-based manifest files.

## 2. Architecture & File Structure

### 2.1 Module Metadata (`b1-module.yaml`)
```yaml
name: xcode
version: 1.0.0
type: development
description: "Xcode IDE management via Tuist. Enables project-as-code and folder-group parity."
skills:
  - name: "Xcode Target Generator"
    description: "Assists in adding new targets to Project.swift (e.g. Unit Tests, Frameworks)."
  - name: "Tuist Manifest Assistant"
    description: "Helps configure dependencies and build settings in Tuist manifests."
hooks:
  post-install: "scripts/post-install.sh"
```

### 2.2 Directory Layout
```
modules/xcode/
├── b1-module.yaml
├── context/
│   ├── best-practices.md
│   ├── conventions.md
│   ├── directory-structure.md
│   ├── project-as-code.md
│   └── signing.md
├── scripts/
│   └── post-install.sh
└── templates/
    └── Project.swift
```

## 3. Core Guidelines (Knowledge Base)

### 3.1 Project-as-Code (`project-as-code.md`)
- **Source of Truth:** `Project.swift` is the absolute source of truth. `.xcodeproj` and `.xcworkspace` files are generated artifacts and should be considered disposable.
- **UI Editing Prohibited:** Never modify project settings (build settings, build phases, target membership) in the Xcode UI. Always modify the Tuist manifests.
- **Syncing:** Run `tuist generate` after any change to the project definition or file structure to synchronize the Xcode environment.

### 3.2 Conventions (`conventions.md`)
- **Naming:** Targets and Groups must follow `PascalCase` (e.g., `AppCore`, `AuthenticationKit`).
- **Cleanliness:** Strict rules against committing developer-specific metadata (`xcuserdata`, `*.xcuserstate`).
- **Modularity:** Encourage splitting logic into focused targets rather than one large "App" target.

### 3.3 Directory Structure (`directory-structure.md`)
- **Standard Layout:**
    - `Project.swift` at the root.
    - `Tuist/` folder for global configuration and templates.
    - `Targets/[TargetName]/` for target-specific source code and resources.
- **Group Parity:** The folder structure on disk must match the group structure in Xcode exactly.

### 3.4 Best Practices (`best-practices.md`)
- **Micro-features:** Guidelines for building a modular app using the micro-features architecture.
- **Build Configuration:** Use `.xcconfig` files for managing environment-specific settings, linked via Tuist.
- **Dependency Management:** Integrate with the `swift` technology module for SPM package dependencies.

### 3.5 Signing & Identity (`signing.md`)
- **Development Signing:** Use automatic signing for local development to minimize setup friction.
- **Config Management:** Define `DEVELOPMENT_TEAM` and `bundleIdPrefix` in the Tuist `Settings` or global configuration.
- **Entitlements:** Manage `.entitlements` files as code and link them explicitly in the target definition.

## 4. Automation & Skills

### 4.1 Hooks
- **`post-install.sh`**: Checks for the existence of `Project.swift` and runs `tuist generate` to ensure the project is ready for development immediately after module installation.

### 4.2 Agent Skills (Conceptual)
- **`Xcode Target Generator`**: An agentic skill that automates the addition of boilerplate for new targets (e.g., creating the folder, adding a `Target` block to `Project.swift`).
- **`Tuist Manifest Assistant`**: Helps navigate the Tuist DSL to add dependencies or modify build settings correctly.

## 5. Success Criteria
1. A valid `modules/xcode/` directory exists with all specified context files.
2. `b1 install modules/xcode` succeeds and registers the module.
3. `post-install` hook successfully triggers `tuist generate` in a project with a valid `Project.swift`.
4. Agent context includes the "Source of Truth" mandate, preventing manual project file edits.
