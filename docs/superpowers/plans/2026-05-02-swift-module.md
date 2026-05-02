# Swift Technology Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a comprehensive b1 module for Swift development that provides language-specific guidelines and automation for SPM projects.

**Architecture:** A standard b1 module structure under `modules/swift/` containing metadata, context markdown files for AI guidance, and a post-install hook for dependency resolution.

**Tech Stack:** b1 (Python-based framework), Swift, Shell.

---

### Task 1: Module Metadata and Structure

**Files:**
- Create: `modules/swift/b1-module.yaml`
- Create: `modules/swift/context/.gitkeep`

- [ ] **Step 1: Create the module config**

```yaml
name: swift
version: 1.0.0
type: development
description: "Core Swift language standards, SPM project structure, and safe concurrency guidelines."
skills:
  - name: "Swift Test Generator"
    description: "Automated XCTest suite generation for Swift functions."
  - name: "Concurrency Refactor"
    description: "Assist in transitioning completion-handlers to async/await."
```

- [ ] **Step 2: Commit structure**

```bash
git add modules/swift/b1-module.yaml
git commit -m "feat(swift): initialize swift module metadata"
```

---

### Task 2: Core Guidelines - Conventions

**Files:**
- Create: `modules/swift/context/conventions.md`

- [ ] **Step 1: Write conventions documentation**

```markdown
# Swift: Coding Conventions

## Naming
- **Types (Classes, Structs, Enums, Protocols):** `PascalCase` — `UserProfile`, `NetworkManager`.
- **Variables, Parameters, Functions:** `camelCase` — `isLoading`, `fetchData()`.
- **Enums Cases:** `camelCase` — `case success`, `case failure(Error)`.
- **Abbreviations:** Avoid them unless they are universal (e.g., `URL`, `ID`). Use `PascalCase` for abbreviations in type names (`URLRequest`, not `UrlRequest`).

## API Design
- Follow official [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/).
- Clarity at the point of use is the most important goal.
- Omit needless words; every word should contribute to clarity.

## Formatting
- Default to `swift-format` defaults.
- Use 4-space indentation.
- Opening braces on the same line.

## Concurrency
- Mandatory use of `async/await` and `Task` for new asynchronous code.
- Prefer `Actors` for isolating shared mutable state.
- Use `MainActor` for code that interacts with the UI.
```

- [ ] **Step 2: Commit**

```bash
git add modules/swift/context/conventions.md
git commit -m "docs(swift): add coding conventions"
```

---

### Task 3: Core Guidelines - Best Practices

**Files:**
- Create: `modules/swift/context/best-practices.md`

- [ ] **Step 1: Write best practices documentation**

```markdown
# Swift: Best Practices

## Design Patterns
- **Protocol-Oriented Programming (POP):** Prefer protocols and extensions for composition over deep class inheritance.
- **Value Types:** Use `struct` and `enum` by default. Value types are safer and more performant.
- **Reference Types:** Use `class` only when you need identity or to interface with Objective-C.

## Error Handling
- Use structured error handling with `do-catch` and custom `Error` enums.
- Prefer throwing errors over returning `nil` or using `Optional` for failures that need explanation.

## Safety
- **Null Safety:** Avoid `!` forced unwrapping. Use `if let`, `guard let`, or nil-coalescing `??`.
- **Exhaustive Switches:** Always use exhaustive `switch` statements for enums to ensure all cases are handled.

## Performance
- Use `final` by default for classes to enable static dispatch.
- Use `private` and `fileprivate` to restrict visibility and aid compiler optimizations.
```

- [ ] **Step 2: Commit**

```bash
git add modules/swift/context/best-practices.md
git commit -m "docs(swift): add best practices"
```

---

### Task 4: Core Guidelines - Structure and Dependencies

**Files:**
- Create: `modules/swift/context/directory-structure.md`
- Create: `modules/swift/context/dependency-management.md`

- [ ] **Step 1: Write directory structure documentation**

```markdown
# Swift: Directory Structure (SPM)

## Standard Layout
```
Project/
├── Package.swift           # Package definition
├── Sources/                # Source code directory
│   └── [TargetName]/       # Target-specific code
│       ├── Main.swift      # Entry point (for executables)
│       └── Models/         # Feature-specific subdirectories
└── Tests/                  # Test suites
    └── [TargetName]Tests/  # Target-specific tests
        └── [TargetName]Tests.swift
```

## Organization
- Keep `Sources/` and `Tests/` directories mirrored.
- Group by feature or module rather than technical layer within a target.
```

- [ ] **Step 2: Write dependency management documentation**

```markdown
# Swift: Dependency Management (SPM)

## Package.swift
- Declare all dependencies in the `dependencies` array of `Package.swift`.
- Use semantic versioning requirements:
  ```swift
  .package(url: "...", from: "1.0.0")
  ```

## Development
- Use `.package(path: "../LocalPackage")` for internal modularization during active development.
- Run `swift package resolve` to fetch dependencies.
- Run `swift package update` to update to the latest compatible versions.
```

- [ ] **Step 3: Commit**

```bash
git add modules/swift/context/directory-structure.md modules/swift/context/dependency-management.md
git commit -m "docs(swift): add structure and dependency guidelines"
```

---

### Task 5: Automation Hooks

**Files:**
- Create: `modules/swift/scripts/post-install.sh`

- [ ] **Step 1: Write post-install script**

```bash
#!/bin/bash
# post-install.sh: Resolve Swift dependencies after module install

if [ -f "Package.swift" ]; then
    echo "📦 Package.swift found. Resolving dependencies..."
    swift package resolve
else
    echo "ℹ️ No Package.swift found in root. Skipping resolution."
fi
```

- [ ] **Step 2: Make script executable**

```bash
chmod +x modules/swift/scripts/post-install.sh
```

- [ ] **Step 3: Update b1-module.yaml with hook**

```yaml
hooks:
  post-install: "scripts/post-install.sh"
```

- [ ] **Step 4: Commit**

```bash
git add modules/swift/scripts/post-install.sh modules/swift/b1-module.yaml
git commit -m "feat(swift): add post-install hook for dependency resolution"
```

---

### Task 6: XCTest Template

**Files:**
- Create: `modules/swift/templates/XCTestTemplate.swift`

- [ ] **Step 1: Create XCTest template**

```swift
import XCTest
@testable import {{TargetName}}

final class {{ClassName}}Tests: XCTestCase {
    
    override func setUpWithError() throws {
        // Put setup code here. This method is called before the invocation of each test method in the class.
    }

    override func tearDownWithError() throws {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
    }

    func testExample() throws {
        // This is an example of a functional test case.
        // Use XCTAssert and related functions to verify your tests produce the correct results.
        XCTAssertTrue(true)
    }

    func testPerformanceExample() throws {
        // This is an example of a performance test case.
        measure {
            // Put the code you want to measure the time of here.
        }
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add modules/swift/templates/XCTestTemplate.swift
git commit -m "feat(swift): add XCTest template"
```

---

### Task 7: Validation

- [ ] **Step 1: Verify module installation locally**

```bash
# In a test project or this one (temporary)
uv run b1 install modules/swift --link
```

- [ ] **Step 2: Check active agents context**

Verify that `GEMINI.md` or `CLAUDE.md` now contains the Swift module context sections.

- [ ] **Step 3: Cleanup and Final Commit**

```bash
git status
# Ensure everything is clean
```
