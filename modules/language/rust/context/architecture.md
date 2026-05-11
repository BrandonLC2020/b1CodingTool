# Rust Architecture and Modules

## Module System
- Prefer file-based modules (`foo.rs`) over directory-based modules (`foo/mod.rs`) for simple namespaces.
- Keep `main.rs` and `lib.rs` thin. Delegate business logic to specific modules.

## Workspaces
- For multi-crate projects, use Cargo Workspaces.
- Keep shared logic in a core `lib` crate and CLI binaries in separate `bin` crates.
