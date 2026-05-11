# Rust Language Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Rust language module with automated skills and core context for CLI tools and systems programming.

**Architecture:** We will create the module structure under `modules/language/rust`. It will include a manifest (`b1-module.yaml`), context files detailing safe systems programming and CLI patterns, skills for crate scaffolding, safety auditing, benchmarking, and error modernization, and basic templates.

**Tech Stack:** Rust, b1 module system, Markdown

---

### Task 1: Create Directory Structure and Manifest

**Files:**
- Create: `modules/language/rust/b1-module.yaml`

- [ ] **Step 1: Create the directory structure**

```bash
mkdir -p modules/language/rust/context
mkdir -p modules/language/rust/skills
mkdir -p modules/language/rust/templates/cli-base/src
```

- [ ] **Step 2: Create the `b1-module.yaml` manifest**

```yaml
# modules/language/rust/b1-module.yaml
name: rust
version: 1.0.0
type: development
description: "Core Rust language guidelines, focusing on high-performance CLI tools and general-purpose systems programming."
skills:
  - name: "Crate Architect"
    description: "Scaffolds a standard workspace or CLI structure with clap and anyhow."
  - name: "Safety Auditor"
    description: "Reviews code for unsafe blocks and interior mutability, suggesting idiomatic safe alternatives."
  - name: "Benchmark Generator"
    description: "Generates criterion or iai benchmark stubs for performance-critical functions."
  - name: "Error Handling Modernizer"
    description: "Refactors legacy error handling to thiserror or anyhow patterns."
```

- [ ] **Step 3: Verify manifest creation**

```bash
cat modules/language/rust/b1-module.yaml
```

- [ ] **Step 4: Commit**

```bash
git add modules/language/rust/b1-module.yaml
git commit -m "feat(rust): add module manifest and structure"
```

---

### Task 2: Create Context Files

**Files:**
- Create: `modules/language/rust/context/safety.md`
- Create: `modules/language/rust/context/cli-patterns.md`
- Create: `modules/language/rust/context/architecture.md`

- [ ] **Step 1: Create `safety.md`**

```markdown
# modules/language/rust/context/safety.md
# Rust Safety and Systems Programming

## Core Philosophy
- **Prefer Safe Rust**: Exhaust all safe alternatives before reaching for `unsafe`.
- **RAII**: Use Resource Acquisition Is Initialization for memory and resource management.

## Unsafe Code
- If `unsafe` is absolutely necessary, it MUST be wrapped in the smallest possible scope.
- Every `unsafe` block MUST be preceded by a `// SAFETY: ` comment explaining why the invariants are upheld.

## Interior Mutability
- Avoid `RefCell` and `Mutex` where simple ownership transfer or structural redesign suffices.
- If shared mutation is required, prefer `parking_lot` for faster locks if appropriate for the domain.
```

- [ ] **Step 2: Create `cli-patterns.md`**

```markdown
# modules/language/rust/context/cli-patterns.md
# CLI Development Patterns

## Argument Parsing
- Standardize on `clap` with the derive API for defining CLI arguments.
- Organize complex commands using subcommands via enums.

## Error Handling
- Use `anyhow::Result` for application-level error returns (e.g., `main` and top-level run functions).
- Use the `Context` trait to add semantic meaning to lower-level errors.

## Logging
- Use `tracing` and `tracing-subscriber` for structured logging instead of `println!`.
```

- [ ] **Step 3: Create `architecture.md`**

```markdown
# modules/language/rust/context/architecture.md
# Rust Architecture and Modules

## Module System
- Prefer file-based modules (`foo.rs`) over directory-based modules (`foo/mod.rs`) for simple namespaces.
- Keep `main.rs` and `lib.rs` thin. Delegate business logic to specific modules.

## Workspaces
- For multi-crate projects, use Cargo Workspaces.
- Keep shared logic in a core `lib` crate and CLI binaries in separate `bin` crates.
```

- [ ] **Step 4: Verify context files**

```bash
ls -l modules/language/rust/context/
```

- [ ] **Step 5: Commit**

```bash
git add modules/language/rust/context/*.md
git commit -m "docs(rust): add core context files"
```

---

### Task 3: Create Skills Instructions

**Files:**
- Create: `modules/language/rust/skills/crate-architect.md`
- Create: `modules/language/rust/skills/safety-auditor.md`
- Create: `modules/language/rust/skills/benchmark-generator.md`
- Create: `modules/language/rust/skills/error-modernizer.md`

- [ ] **Step 1: Create `crate-architect.md`**

```markdown
# modules/language/rust/skills/crate-architect.md
# Crate Architect Skill

When invoked to scaffold a new CLI or workspace:

1. Identify if the user wants a simple CLI or a workspace.
2. For a simple CLI, copy the contents of `templates/cli-base/` into the target directory.
3. Replace placeholders like `{{crate_name}}` with the actual name.
4. Ensure `clap`, `anyhow`, and `tokio` (if async) are in `Cargo.toml`.
5. Run `cargo check` to verify the scaffold compiles.
```

- [ ] **Step 2: Create `safety-auditor.md`**

```markdown
# modules/language/rust/skills/safety-auditor.md
# Safety Auditor Skill

When invoked to review code:

1. Scan the target files for `unsafe { ... }` blocks.
2. For each block, verify the presence of a `// SAFETY: ` comment. If missing, flag it.
3. Scan for `RefCell`, `Mutex`, and `RwLock`. 
4. Suggest architectural changes (e.g., message passing, restructuring lifetimes) that could eliminate the need for interior mutability.
5. Provide a summary report of findings and actionable refactoring steps.
```

- [ ] **Step 3: Create `benchmark-generator.md`**

```markdown
# modules/language/rust/skills/benchmark-generator.md
# Benchmark Generator Skill

When invoked to create benchmarks for a target function:

1. Create a `benches/` directory at the crate root if it doesn't exist.
2. Add `[dev-dependencies]` for `criterion` to `Cargo.toml`.
3. Add a `[[bench]]` section to `Cargo.toml`.
4. Create a stub `benches/my_benchmark.rs` that imports the target function and sets up a basic Criterion group.
5. Provide instructions to the user to run `cargo bench`.
```

- [ ] **Step 4: Create `error-modernizer.md`**

```markdown
# modules/language/rust/skills/error-modernizer.md
# Error Handling Modernizer Skill

When invoked to refactor error handling:

1. Determine if the target is a library or an application.
2. For libraries: Refactor custom enum errors to use `thiserror::Error`. Replace manual `Display` and `Error` trait implementations.
3. For applications: Refactor functions returning `Result<T, Box<dyn Error>>` or custom errors to return `anyhow::Result<T>`.
4. Inject `.context("...")` calls where lower-level errors are propagated to add meaningful information.
```

- [ ] **Step 5: Verify skills files**

```bash
ls -l modules/language/rust/skills/
```

- [ ] **Step 6: Commit**

```bash
git add modules/language/rust/skills/*.md
git commit -m "feat(rust): add skill instruction files"
```

---

### Task 4: Create Templates and Verification

**Files:**
- Create: `modules/language/rust/templates/cli-base/Cargo.toml`
- Create: `modules/language/rust/templates/cli-base/src/main.rs`

- [ ] **Step 1: Create template `Cargo.toml`**

```toml
# modules/language/rust/templates/cli-base/Cargo.toml
[package]
name = "{{crate_name}}"
version = "0.1.0"
edition = "2021"

[dependencies]
anyhow = "1.0"
clap = { version = "4.5", features = ["derive"] }
tracing = "0.1"
tracing-subscriber = "0.3"
```

- [ ] **Step 2: Create template `main.rs`**

```rust
// modules/language/rust/templates/cli-base/src/main.rs
use anyhow::{Context, Result};
use clap::Parser;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Name of the person to greet
    #[arg(short, long)]
    name: String,
}

fn main() -> Result<()> {
    tracing_subscriber::fmt::init();

    let args = Args::parse();
    
    // Example of context usage
    run(&args.name).context("Failed to execute run logic")?;

    Ok(())
}

fn run(name: &str) -> Result<()> {
    println!("Hello, {}!", name);
    Ok(())
}
```

- [ ] **Step 3: Verification Check**
Run the module installer in a dry-run fashion or perform manual validation to ensure the manifest parses correctly.

```bash
# Verify all files exist
find modules/language/rust
```

- [ ] **Step 4: Commit**

```bash
git add modules/language/rust/templates/
git commit -m "feat(rust): add cli-base template"
```
