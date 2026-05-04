# Swift: Directory Structure (SPM)

## Standard Layout
```
Project/
├── Package.swift           # Package definition
├── Sources/                # Source code directory
│   └── [TargetName]/       # Target-specific code
│       ├── main.swift      # Entry point (for executables)
│       └── Models/         # Feature-specific subdirectories
└── Tests/                  # Test suites
    └── [TargetName]Tests/  # Target-specific tests
        └── [TargetName]Tests.swift
```

## Organization
- Keep `Sources/` and `Tests/` directories mirrored.
- Group by feature or module rather than technical layer within a target.
