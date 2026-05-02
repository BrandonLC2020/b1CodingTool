# Xcode: Directory Structure (Tuist)

## Standard Layout
```
Project/
├── Project.swift           # Main project definition
├── Tuist/                  # Tuist configuration and templates
│   ├── Config.swift
│   ├── ProjectDescriptionHelpers/
│   └── Templates/
├── Targets/                # Source code for all targets
│   └── [TargetName]/
│       ├── Sources/
│       ├── Resources/
│       └── Tests/
└── Derived/                # Generated files (ignored)
```

## Group Parity
- The folder structure in `Targets/` must map 1:1 to the groups displayed in Xcode.
