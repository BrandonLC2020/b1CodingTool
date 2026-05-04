# Xcode: Project-as-Code (Tuist)

## The Source of Truth
- **Manifest First:** `Project.swift` is the absolute source of truth for the project structure.
- **Disposable Artifacts:** `.xcodeproj` and `.xcworkspace` files are generated artifacts. They should NOT be modified manually and should NOT be committed to version control.
- **Synchronization:** Run `tuist generate` after any change to the project definition (`Project.swift`, `Targets/`, etc.) or physical file structure.

## UI Editing Prohibited
- Never modify target membership, build phases, or build settings via the Xcode UI. These changes will be overwritten the next time the project is generated.
- Any change that affects the project file must be done in the Swift manifests.
