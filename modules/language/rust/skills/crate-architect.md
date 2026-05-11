# Crate Architect Skill

When invoked to scaffold a new CLI or workspace:

1. Identify if the user wants a simple CLI or a workspace.
2. For a simple CLI, copy the contents of `templates/cli-base/` into the target directory.
3. Replace placeholders like `{{crate_name}}` with the actual name.
4. Ensure `clap`, `anyhow`, and `tokio` (if async) are in `Cargo.toml`.
5. Run `cargo check` to verify the scaffold compiles.
