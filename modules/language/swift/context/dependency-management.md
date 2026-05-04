# Swift: Dependency Management (SPM)

## Package.swift
- Declare all dependencies in the `dependencies` array of `Package.swift`.
- Use semantic versioning requirements:
  ```swift
  .package(url: "...", from: "1.0.0")
  ```

## Development
- Use `.package(path: "../LocalPackage")` for internal modularization during active development.
- Run `swift package resolve` to fetch dependencies.
- Run `swift package update` to update to the latest compatible versions.
