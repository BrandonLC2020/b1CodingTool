# SwiftUI: Conventions

## Naming
- **Views:** Use `PascalCase` with a `View` suffix (e.g., `HomeView`, `UserCellView`).
- **View Modifiers:** Use `camelCase` and keep them descriptive (e.g., `primaryButtonStyle()`).
- **State Variables:** Use `camelCase` (e.g., `isLoading`, `userInput`).

## File Organization
- **One View per File:** Each non-trivial SwiftUI view should reside in its own file named after the view.
- **Preview Support:** Keep `Previews` at the bottom of the same file as the view.
- **Extensions:** Place view-specific modifiers in an `Extension` block at the end of the file or in a dedicated `ViewModifiers.swift` file.

## Code Style
- **Modifier Order:** Order modifiers consistently:
    1. Layout (e.g., `frame`, `padding`)
    2. Styling (e.g., `background`, `clipShape`)
    3. Interactions (e.g., `onTapGesture`)
    4. Accessibility (e.g., `accessibilityLabel`)
- **Trailing Closures:** Always use trailing closure syntax for `VStack`, `HStack`, etc.
- **Explicit Types:** Only provide explicit types for properties when Swift's inference is ambiguous or for public APIs.
