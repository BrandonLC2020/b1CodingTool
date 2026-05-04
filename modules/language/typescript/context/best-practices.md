# TypeScript: Best Practices

## Type Safety
- **Strict Mode:** Always enable `strict: true` in `tsconfig.json`.
- **Avoid `any`:** Use `unknown` or specific interfaces instead of `any`. If a value is genuinely dynamic, use type guards or Zod for validation.
- **Interfaces vs. Types:** Prefer `interface` for public APIs and object structures (as they support extension/merging) and `type` for unions, intersections, and primitives.
- **Utility Types:** Leverage built-in utility types (e.g., `Partial`, `Pick`, `Omit`, `Readonly`) to maintain type flexibility.

## Code Quality
- **Explicit Returns:** Annotate return types for all public-facing functions and complex logic.
- **Immutability:** Use `readonly` for array and object properties that should not be modified.
- **Enums:** Prefer `const enum` or string unions over standard `enum` to minimize runtime overhead.

## Error Handling
- **Type Guards:** Use `is` predicates to safely narrow types in catch blocks.
- **Custom Errors:** Extend the base `Error` class for domain-specific exceptions.
- **Result Pattern:** For critical operations, consider returning a Result object (e.g., `{ success: true, data: T } | { success: false, error: Error }`).

## Performance
- **Tree Shaking:** Use ESM (`import`/`export`) to allow bundlers to remove unused code.
- **Type-only Imports:** Use `import type { ... }` for types to ensure they are fully stripped during compilation.
