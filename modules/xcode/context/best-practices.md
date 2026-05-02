# Xcode: Best Practices

## Modularity
- **Micro-features:** Organize the app into modular components: `Feature`, `Domain`, `Core`, and `Foundation`.
- **Interface Targets:** Use separate interface targets for large modules to minimize build dependencies.

## Build Settings
- **XCConfigs:** Use `.xcconfig` files for build settings that vary by environment (e.g., Debug vs. Release).
- **Hardcoding:** Avoid hardcoding paths or flags in `Project.swift` if they can be handled via xcconfigs.

## Dependency Management
- **SPM Integration:** Link SPM packages via the `dependencies` array in `Project.swift`.
- **Internal Dependencies:** Use target references for dependencies between internal modules.
