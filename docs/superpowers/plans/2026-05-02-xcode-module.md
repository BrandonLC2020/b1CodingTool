# Xcode IDE Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a comprehensive b1 module for Xcode IDE management using Tuist to enable "Project-as-Code" workflows.

**Architecture:** A standard b1 module structure under `modules/xcode/` containing metadata, context markdown files for AI guidance on Tuist standards, and a post-install hook for automatic project generation.

**Tech Stack:** b1 (Python-based framework), Tuist (Swift-based project generator), Shell.

---

### Task 1: Module Metadata and Structure

**Files:**
- Create: `modules/xcode/b1-module.yaml`
- Create: `modules/xcode/context/.gitkeep`

- [ ] **Step 1: Create the module config**

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
```

- [ ] **Step 2: Commit structure**

```bash
git add modules/xcode/b1-module.yaml
git commit -m "feat(xcode): initialize xcode module metadata"
```

---

### Task 2: Core Guidelines - Project-as-Code & Conventions

**Files:**
- Create: `modules/xcode/context/project-as-code.md`
- Create: `modules/xcode/context/conventions.md`

- [ ] **Step 1: Write project-as-code documentation**

```markdown
# Xcode: Project-as-Code (Tuist)

## The Source of Truth
- **Manifest First:** `Project.swift` is the absolute source of truth for the project structure.
- **Disposable Artifacts:** `.xcodeproj` and `.xcworkspace` files are generated artifacts. They should NOT be modified manually and should NOT be committed to version control.
- **Synchronization:** Run `tuist generate` after any change to the project definition (`Project.swift`, `Targets/`, etc.) or physical file structure.

## UI Editing Prohibited
- Never modify target membership, build phases, or build settings via the Xcode UI. These changes will be overwritten the next time the project is generated.
- Any change that affects the project file must be done in the Swift manifests.
```

- [ ] **Step 2: Write conventions documentation**

```markdown
# Xcode: Coding Conventions

## Naming
- **Targets:** Use `PascalCase` (e.g., `FeatureHome`, `CoreNetwork`).
- **Groups:** Must match physical folder names exactly.
- **Schemes:** Shared schemes should be defined in `Project.swift`.

## Cleanliness
- **Metadata:** Never commit `xcuserdata`, `*.xcuserstate`, or `DerivedData`.
- **Modularity:** Prefer many small targets (frameworks) over a single large application target. This improves build times and enforces clear boundaries.
```

- [ ] **Step 3: Commit**

```bash
git add modules/xcode/context/project-as-code.md modules/xcode/context/conventions.md
git commit -m "docs(xcode): add project-as-code and convention guidelines"
```

---

### Task 3: Core Guidelines - Structure & Best Practices

**Files:**
- Create: `modules/xcode/context/directory-structure.md`
- Create: `modules/xcode/context/best-practices.md`

- [ ] **Step 1: Write directory structure documentation**

```markdown
# Xcode: Directory Structure (Tuist)

## Standard Layout
```
Project/
├── Project.swift           # Main project definition
├── Tuist/                  # Tuist configuration and templates
│   ├── Config.swift
│   ├── ProjectDescriptionHelpers/
│   └── Templates/
├── Targets/                # Source code for all targets
│   └── [TargetName]/
│       ├── Sources/
│       ├── Resources/
│       └── Tests/
└── Derived/                # Generated files (ignored)
```

## Group Parity
- The folder structure in `Targets/` must map 1:1 to the groups displayed in Xcode.
```

- [ ] **Step 2: Write best practices documentation**

```markdown
# Xcode: Best Practices

## Modularity
- **Micro-features:** Organize the app into modular components: `Feature`, `Domain`, `Core`, and `Foundation`.
- **Interface Targets:** Use separate interface targets for large modules to minimize build dependencies.

## Build Settings
- **XCConfigs:** Use `.xcconfig` files for build settings that vary by environment (e.g., Debug vs. Release).
- **Hardcoding:** Avoid hardcoding paths or flags in `Project.swift` if they can be handled via xcconfigs.

## Dependency Management
- **SPM Integration:** Link SPM packages via the `dependencies` array in `Project.swift`.
- **Internal Dependencies:** Use target references for dependencies between internal modules.
```

- [ ] **Step 3: Commit**

```bash
git add modules/xcode/context/directory-structure.md modules/xcode/context/best-practices.md
git commit -m "docs(xcode): add structure and best practice guidelines"
```

---

### Task 4: Core Guidelines - Signing & Identity

**Files:**
- Create: `modules/xcode/context/signing.md`

- [ ] **Step 1: Write signing documentation**

```markdown
# Xcode: Signing & Identity

## Development Signing
- **Automatic Signing:** Use Xcode's automatic signing for local development.
- **Config:** Specify the `DEVELOPMENT_TEAM` and `ORGANIZATION_NAME` in the `Settings` block of `Project.swift`.

## Configuration Management
- **Bundle IDs:** Define a `bundleIdPrefix` (e.g., `com.mycompany`) and derive target bundle IDs programmatically in the manifest.
- **Entitlements:** Store `.entitlements` files in the target's folder and link them explicitly in `Project.swift`.

## Security
- Never commit distribution certificates or provisioning profiles to the repository.
- Use environment variables or secure vault storage for CI/CD signing identities.
```

- [ ] **Step 2: Commit**

```bash
git add modules/xcode/context/signing.md
git commit -m "docs(xcode): add signing and identity guidelines"
```

---

### Task 5: Automation Hooks

**Files:**
- Create: `modules/xcode/scripts/post-install.sh`
- Modify: `modules/xcode/b1-module.yaml`

- [ ] **Step 1: Write post-install script**

```bash
#!/bin/bash
# post-install.sh: Generate Xcode project via Tuist after module install

if [ -f "Project.swift" ]; then
    echo "🏗️ Project.swift found. Generating Xcode project via Tuist..."
    if command -v tuist &> /dev/null; then
        tuist generate
    else
        echo "⚠️ Tuist not found. Please install Tuist to generate the project."
    fi
else
    echo "ℹ️ No Project.swift found in root. Skipping project generation."
fi
```

- [ ] **Step 2: Make script executable**

```bash
chmod +x modules/xcode/scripts/post-install.sh
```

- [ ] **Step 3: Update b1-module.yaml with hook**

```yaml
hooks:
  post-install: "scripts/post-install.sh"
```

- [ ] **Step 4: Commit**

```bash
git add modules/xcode/scripts/post-install.sh modules/xcode/b1-module.yaml
git commit -m "feat(xcode): add post-install hook for Tuist generation"
```

---

### Task 6: Project.swift Template

**Files:**
- Create: `modules/xcode/templates/Project.swift`

- [ ] **Step 1: Create Tuist template**

```swift
import ProjectDescription

let project = Project(
    name: "{{ProjectName}}",
    organizationName: "{{OrganizationName}}",
    settings: .settings(
        base: [
            "DEVELOPMENT_TEAM": "{{DevelopmentTeam}}"
        ]
    ),
    targets: [
        .target(
            name: "{{ProjectName}}",
            destinations: .iOS,
            product: .app,
            bundleId: "{{BundleIdPrefix}}.{{ProjectName}}",
            infoPlist: .default,
            sources: ["Targets/{{ProjectName}}/Sources/**"],
            resources: ["Targets/{{ProjectName}}/Resources/**"],
            dependencies: []
        ),
        .target(
            name: "{{ProjectName}}Tests",
            destinations: .iOS,
            product: .unitTests,
            bundleId: "{{BundleIdPrefix}}.{{ProjectName}}Tests",
            infoPlist: .default,
            sources: ["Targets/{{ProjectName}}/Tests/**"],
            dependencies: [
                .target(name: "{{ProjectName}}")
            ]
        ),
    ]
)
```

- [ ] **Step 2: Commit**

```bash
git add modules/xcode/templates/Project.swift
git commit -m "feat(xcode): add Project.swift template"
```

---

### Task 7: Validation

- [ ] **Step 1: Verify module installation locally**

```bash
uv run b1 install modules/xcode --link
```

- [ ] **Step 2: Check active agents context**

Verify that `GEMINI.md` or `CLAUDE.md` now contains the Xcode module context sections.

- [ ] **Step 3: Final Commit and cleanup**

```bash
git status
```
