# Design Spec: Rust Language Module

**Date:** 2026-05-11  
**Status:** Approved  
**Topic:** Language Module implementation for Rust.

## 1. Goal
Implement a `rust` language module for the `b1CodingTool` that provides high-quality context and automated skills for building high-performance CLI tools and general-purpose systems programming.

## 2. Architecture
The module will reside in `modules/language/rust/` and follow the standard `b1` module anatomy.

### 2.1 Directory Structure
```text
modules/language/rust/
├── b1-module.yaml      # Manifest defining identity and skills
├── context/            # Markdown files for agent memory
│   ├── safety.md       # Ownership, borrowing, and unsafe rules
│   ├── cli-patterns.md # Clap, anyhow, and logging best practices
│   └── architecture.md # Module system and workspace guidelines
├── skills/             # Instructions for specific agent tasks
│   ├── crate-architect.md
│   ├── safety-auditor.md
│   ├── benchmark-generator.md
│   └── error-modernizer.md
└── templates/          # Scaffolding files
    └── cli-base/       # Basic Cargo.toml + main.rs with clap
```

## 3. Skills Definition

### 3.1 Crate Architect
- **Purpose**: Scaffold a standard workspace or CLI structure.
- **Tools**: `clap` (derive), `anyhow`, `serde`.
- **Output**: Pre-configured `Cargo.toml` and directory layout.

### 3.2 Safety Auditor
- **Purpose**: Review code for `unsafe` blocks and interior mutability.
- **Focus**: Suggesting idiomatic safe alternatives and ensuring `unsafe` is documented.

### 3.3 Benchmark Generator
- **Purpose**: Generate `criterion` or `iai` benchmark stubs.
- **Focus**: Performance-critical paths and comparison testing.

### 3.4 Error Handling Modernizer
- **Purpose**: Refactor legacy error handling to `thiserror` or `anyhow`.
- **Focus**: Consistent error propagation and user-friendly messaging.

## 4. Context Guidelines
- **Safety**: Prefer safe Rust; `unsafe` is a last resort.
- **Performance**: Zero-cost abstractions and RAII.
- **CLI**: Standardize on `clap` and `anyhow`.

## 5. Verification Plan
1. **Structural Validation**: Ensure `b1-module.yaml` follows the schema in `MODULE_GUIDE.md`.
2. **Integration Test**: Run `b1 install --link` and verify `agent.md` compilation.
3. **Skill Verification**: Manually prompt the agent to perform a "Safety Audit" on a sample file.
