# Python: Directory Structure

## Standard Package Layout
```
project_root/
├── pyproject.toml         # Build system and dependency config
├── README.md
├── src/                   # Source code
│   └── package_name/      # Main package
│       ├── __init__.py
│       ├── main.py        # Entry point
│       └── utils.py
├── tests/                 # Test suites (pytest)
│   ├── conftest.py
│   └── unit/
└── docs/                  # Project documentation
```

## Scoped Modules
- For larger projects, use a `features/` or `core/` subdirectory to organize logic by domain rather than layer.
