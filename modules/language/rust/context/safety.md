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
