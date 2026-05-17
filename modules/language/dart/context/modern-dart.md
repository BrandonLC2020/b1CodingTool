# Modern Dart (3.x+) Guidelines

## Pattern Matching & Records
- **Records:** Use for multiple return values: `(double lat, double lon) getLocation()`.
- **Destructuring:** Use pattern matching to unpack records: `var (lat, lon) = getLocation();`.

## Sealed Hierarchies
- **Sealed Classes:** Use `sealed` for Restricted Class Hierarchies (e.g., UI States).
- **Exhaustive Switches:** Leverage compiler-checked exhaustive switching on sealed types.

## Null Safety
- **Soundness:** Assume code is soundly null-safe.
- **Avoid `!`:** Prefer `if (x != null)` or `??` over the bang operator.
- **Late:** Use `late` only when initialization is guaranteed before first access.
