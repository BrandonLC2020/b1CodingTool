# Dart: Coding Conventions

## Naming Standards
- **Classes, Enums, Typedefs, Type Parameters:** `PascalCase`.
- **Libraries, Packages, Directories, Source Files:** `snake_case`.
- **Variables, Parameters, Named Parameters, Constants:** `camelCase`.
- **Private Members:** Prefix with an underscore `_`.

## Formatting
- **Standard:** Use `dart format .` exclusively.
- **Line Length:** 80 characters.
- **Indentation:** 2 spaces.

## Best Practices
- **Prefer `final`:** Use `final` for variables that aren't reassigned.
- **Arrow Syntax:** Use `=>` for single-line functions or getters.
- **Strings:** Use adjacent string literals for concatenation, not `+`.

## Linting
- **Standard:** Standardize on `package:lints/recommended.yaml`.
