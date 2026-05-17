# Dart: Testing Standards

## Setup
- **Directory:** All tests must reside in the `test/` folder.
- **Naming:** Files must end in `_test.dart`.

## Framework (package:test)
- **Grouping:** Use `group()` to organize related tests.
- **Assertions:** Use `expect(actual, matcher)`.
- **Async:** Use `test(...) async` for logic and stream verification.

## Mocking
- **Preferred:** Use `mocktail` for type-safe mocking without code generation.
- **Fakes:** Prefer simple `Fake` class implementations for data repositories.
