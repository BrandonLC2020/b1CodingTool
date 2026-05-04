# Swift: Coding Conventions

## Naming
- **Types (Classes, Structs, Enums, Protocols):** `PascalCase` — `UserProfile`, `NetworkManager`.
- **Variables, Parameters, Functions:** `camelCase` — `isLoading`, `fetchData()`.
- **Enums Cases:** `camelCase` — `case success`, `case failure(Error)`.
- **Abbreviations:** Avoid them unless they are universal (e.g., `URL`, `ID`). Use `PascalCase` for abbreviations in type names (`URLRequest`, not `UrlRequest`).

## API Design
- Follow official [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/).
- Clarity at the point of use is the most important goal.
- Omit needless words; every word should contribute to clarity.

## Formatting
- Default to `swift-format` defaults.
- Use 4-space indentation.
- Opening braces on the same line.

## Concurrency
- Mandatory use of `async/await` and `Task` for new asynchronous code.
- Prefer `Actors` for isolating shared mutable state.
- Use `MainActor` for code that interacts with the UI.
