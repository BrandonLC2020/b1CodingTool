# Error Handling Modernizer Skill

When invoked to refactor error handling:

1. Determine if the target is a library or an application.
2. For libraries: Refactor custom enum errors to use `thiserror::Error`. Replace manual `Display` and `Error` trait implementations.
3. For applications: Refactor functions returning `Result<T, Box<dyn Error>>` or custom errors to return `anyhow::Result<T>`.
4. Inject `.context("...")` calls where lower-level errors are propagated to add meaningful information.
