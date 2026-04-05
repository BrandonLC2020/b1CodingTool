# Flutter: Best Practices

## Widget Composition
- **Extract early.** If a widget's `build()` method exceeds ~40 lines or nests more than 3 levels deep, extract subtrees into their own widget classes (not private methods — widget classes get their own element node and rebuild independently).
- Prefer `StatelessWidget` over `StatefulWidget` unless local ephemeral state is truly needed. Lift persistent or shared state to providers.
- Never call `setState()` from `initState()` directly; use `WidgetsBinding.instance.addPostFrameCallback` if a post-frame update is needed.

## State Management (Riverpod)
- Use `flutter_riverpod` as the default state management solution.
- Declare providers at the top level (not inside widgets or functions).
- Use `AsyncNotifierProvider` for async state; `NotifierProvider` for sync state.
- Use `ref.watch()` inside `build()`; use `ref.read()` inside callbacks and methods.
- Never store a `WidgetRef` — it may become stale. Pass `ref` down or use a callback.

```dart
// Good
final userProvider = AsyncNotifierProvider<UserNotifier, User>(UserNotifier.new);

class UserNotifier extends AsyncNotifier<User> {
  @override
  Future<User> build() => ref.watch(userRepositoryProvider).fetchCurrentUser();
}

// In widget
@override
Widget build(BuildContext context, WidgetRef ref) {
  final user = ref.watch(userProvider);
  return user.when(
    data: (u) => Text(u.name),
    loading: () => const CircularProgressIndicator(),
    error: (e, _) => Text('Error: $e'),
  );
}
```

## Performance
- Use `const` widgets aggressively — they are never rebuilt.
- Use `ListView.builder` (lazy) rather than `ListView` (eager) for any list that could have more than ~20 items.
- Use `RepaintBoundary` around expensive, frequently-repainting subtrees (e.g., animations).
- Avoid doing work in `build()` — compute derived values in the provider, not the widget.
- Profile with Flutter DevTools before optimizing; don't guess.

## Async & BuildContext
- After any `await`, check `if (!mounted) return;` before using `context`.
- Never pass `BuildContext` across isolate boundaries.
- Use `FutureBuilder` or Riverpod's `AsyncValue` rather than storing Future results in `setState`.

```dart
// Good
Future<void> _save() async {
  await repository.save(data);
  if (!mounted) return;
  ScaffoldMessenger.of(context).showSnackBar(...);
}
```

## Navigation
- Use `go_router` for all routing. Define all routes in a single `router.dart` file.
- Use named routes (`context.goNamed('profile')`) not path strings scattered through the code.
- Pass typed data via `extra` or route parameters, not global state.

## Error Handling
- Surface errors through `AsyncValue.error` in providers — do not swallow exceptions silently.
- Show user-facing errors in a `SnackBar` or dedicated error widget; log technical details.
- Use a root `ProviderScope` `overrides` + `ErrorWidget.builder` for uncaught widget errors in production.

## Testing
- Write **widget tests** for UI components using `testWidgets` + `WidgetTester`.
- Write **unit tests** for all Notifiers/business logic with `ProviderContainer` (no Flutter framework needed).
- Use **golden tests** sparingly — only for design-critical components.
- Prefer `Fake` objects over `Mock` objects to avoid brittle test coupling.

```dart
test('UserNotifier emits user on load', () async {
  final container = ProviderContainer(overrides: [
    userRepositoryProvider.overrideWithValue(FakeUserRepository()),
  ]);
  addTearDown(container.dispose);
  await expectLater(
    container.read(userProvider.future),
    completion(isA<User>()),
  );
});
```
