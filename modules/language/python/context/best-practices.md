# Python: Best Practices

## Code Quality
- **Type Hinting:** Use PEP 484 type hints for all function signatures and complex variables. Use `from __future__ import annotations` to support forward references.
- **KISS & DRY:** Prioritize readability. Pythonic code (idiomatic) is preferred over complex abstractions.
- **Docstrings:** Use Google-style or NumPy-style docstrings for all public modules, classes, and functions.

## Error Handling
- **Specific Exceptions:** Catch specific exceptions rather than using a blanket `except Exception:`.
- **EAFP (Easier to Ask for Forgiveness than Permission):** Prefer `try-except` blocks over pre-emptive checks where appropriate.
- **Custom Exceptions:** Create domain-specific exception classes for complex logic.

## Concurrency
- **Async/Await:** Use `asyncio` for I/O-bound tasks.
- **Subprocessing:** Use the `subprocess` module for running external commands, ensuring proper timeout and error handling.
- **Threading/Multiprocessing:** Use `threading` for I/O and `multiprocessing` for CPU-bound tasks, adhering to the Global Interpreter Lock (GIL) constraints.

## Performance
- **Built-in Functions:** Prefer built-in functions and standard library modules (e.g., `itertools`, `collections`) as they are highly optimized.
- **Profiling:** Use `cProfile` or `timeit` to identify bottlenecks before optimizing.
