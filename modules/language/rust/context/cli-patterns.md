# CLI Development Patterns

## Argument Parsing
- Standardize on `clap` with the derive API for defining CLI arguments.
- Organize complex commands using subcommands via enums.

## Error Handling
- Use `anyhow::Result` for application-level error returns (e.g., `main` and top-level run functions).
- Use the `Context` trait to add semantic meaning to lower-level errors.

## Logging
- Use `tracing` and `tracing-subscriber` for structured logging instead of `println!`.
