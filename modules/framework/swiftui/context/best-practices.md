# SwiftUI: Best Practices

## View Composition
- **Small is Beautiful:** Extract subviews liberally. If a `body` property exceeds 30-40 lines, it's a candidate for extraction into a separate `struct`.
- **View Hierarchy:** Prefer `Group` or `@ViewBuilder` for logic-heavy views to avoid deep nesting of `if/else` inside containers.
- **Computed Properties:** Use private computed properties for simple sub-elements that don't need their own state.

## State Management (Modern)
- **Local State:** Use `@State` for private, simple data owned by the view.
- **Shared State:** Use the `@Observable` macro (Swift 5.9+) for complex models. Avoid `ObservableObject` and `@Published` in new code.
- **Data Flow:** Pass data down via initializers; use `@Environment` for cross-cutting concerns (e.g., theme, user session).
- **Binding:** Use `@Binding` to create a two-way connection to state owned by a parent view.

## Performance
- **Identify Stability:** Ensure your data models are stable to prevent unnecessary view body evaluations.
- **Previews:** Always include `Preview` providers. Use mock data to test various states (loading, error, empty).
- **Heavy Work:** Never perform network calls or heavy computation directly in a view initializer or `body`. Use `.task` or `.onAppear`.

## Layout
- **Containers:** Use `VStack`, `HStack`, and `ZStack` as primary building blocks.
- **Adaptive Layout:** Use `Spacer`, `layoutPriority()`, and `GeometryReader` (sparingly) to create responsive UIs.
- **Safe Areas:** Respect safe areas unless a background element explicitly needs to ignore them.
