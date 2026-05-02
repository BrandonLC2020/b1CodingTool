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
