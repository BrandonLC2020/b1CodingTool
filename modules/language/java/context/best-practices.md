# Java: Best Practices

## Design Patterns
- **SOLID Principles:** Adhere strictly to SOLID principles.
- **Composition over Inheritance:** Prefer composition to build flexible systems.
- **Factory & Singleton:** Use design patterns like Factory, Singleton, and Builder where appropriate.

## Code Quality
- **Type Safety:** Leverage Java's strong typing. Avoid using `Object` or raw types.
- **Immutability:** Use `final` for variables and parameters that do not change. Prefer immutable collections.
- **Java Streams:** Use Stream API for cleaner, declarative collection processing.

## Error Handling
- **Specific Exceptions:** Throw and catch specific exceptions. Avoid `catch (Exception e)`.
- **Checked vs. Unchecked:** Use checked exceptions for recoverable errors and unchecked for programming errors.
- **Optional:** Use `Optional<T>` to avoid `null` returns and `NullPointerException`.

## Performance
- **JVM Optimization:** Be aware of GC (Garbage Collection) behavior. Avoid creating unnecessary objects in hot loops.
- **String Building:** Use `StringBuilder` for string concatenation in loops.
- **Concurrency:** Use `java.util.concurrent` (Executors, CompletableFuture, Virtual Threads in Java 21+) for multi-threaded tasks.
