# Benchmark Generator Skill

When invoked to create benchmarks for a target function:

1. Create a `benches/` directory at the crate root if it doesn't exist.
2. Add `[dev-dependencies]` for `criterion` to `Cargo.toml`.
3. Add a `[[bench]]` section to `Cargo.toml`.
4. Create a stub `benches/my_benchmark.rs` that imports the target function and sets up a basic Criterion group.
5. Provide instructions to the user to run `cargo bench`.
