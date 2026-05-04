# Xcode: Coding Conventions

## Naming
- **Targets:** Use `PascalCase` (e.g., `FeatureHome`, `CoreNetwork`).
- **Groups:** Must match physical folder names exactly.
- **Schemes:** Shared schemes should be defined in `Project.swift`.

## Cleanliness
- **Metadata:** Never commit `xcuserdata`, `*.xcuserstate`, or `DerivedData`.
- **Modularity:** Prefer many small targets (frameworks) over a single large application target. This improves build times and enforces clear boundaries.
