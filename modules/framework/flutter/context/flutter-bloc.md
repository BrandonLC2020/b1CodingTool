# Flutter: State Management with flutter_bloc

## Core Concepts

`flutter_bloc` separates state management into three layers:

- **Event** — an immutable description of something that happened (user action, data loaded, error received)
- **Bloc** — receives events, runs business logic, emits new states
- **State** — an immutable snapshot of what the UI should render

For simple cases without events, use a **Cubit** instead — it exposes methods that directly emit states, skipping the event dispatch layer.

```
UI dispatches Event → Bloc maps Event → State → UI rebuilds
UI calls method     → Cubit emits State         → UI rebuilds
```

**Rule of thumb:** Use `Cubit` when the state transitions are simple and linear. Use `Bloc` when you need to react to a stream of events, debounce/throttle input, or have complex branching logic.

## Defining Events and States

Use sealed classes (Dart 3+) for both events and states. Sealed classes give you exhaustive pattern matching in `switch` expressions.

```dart
// events
sealed class AuthEvent {}
final class AuthLoginRequested extends AuthEvent {
  const AuthLoginRequested({required this.email, required this.password});
  final String email;
  final String password;
}
final class AuthLogoutRequested extends AuthEvent {}

// states
sealed class AuthState {}
final class AuthInitial extends AuthState {}
final class AuthLoading extends AuthState {}
final class AuthAuthenticated extends AuthState {
  const AuthAuthenticated(this.user);
  final User user;
}
final class AuthFailure extends AuthState {
  const AuthFailure(this.message);
  final String message;
}
```

## Writing a Bloc

```dart
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc({required AuthRepository authRepository})
      : _authRepository = authRepository,
        super(AuthInitial()) {
    on<AuthLoginRequested>(_onLoginRequested);
    on<AuthLogoutRequested>(_onLogoutRequested);
  }

  final AuthRepository _authRepository;

  Future<void> _onLoginRequested(
    AuthLoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final user = await _authRepository.login(event.email, event.password);
      emit(AuthAuthenticated(user));
    } catch (e) {
      emit(AuthFailure(e.toString()));
    }
  }

  Future<void> _onLogoutRequested(
    AuthLogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    await _authRepository.logout();
    emit(AuthInitial());
  }
}
```

## Writing a Cubit

```dart
class CounterCubit extends Cubit<int> {
  CounterCubit() : super(0);

  void increment() => emit(state + 1);
  void decrement() => emit(state - 1);
  void reset() => emit(0);
}
```

## Providing Blocs and Cubits

Use `BlocProvider` to create and scope a Bloc to a widget subtree. The Bloc is automatically closed when the subtree is removed from the tree.

```dart
// Single bloc
BlocProvider(
  create: (context) => AuthBloc(authRepository: context.read()),
  child: const LoginPage(),
)

// Multiple blocs at app root
MultiBlocProvider(
  providers: [
    BlocProvider(create: (context) => AuthBloc(authRepository: context.read())),
    BlocProvider(create: (context) => ThemeCubit()),
  ],
  child: const App(),
)
```

Never create a Bloc inside a `build()` method — it will be recreated on every rebuild. Always use `BlocProvider` or create the Bloc above the widget tree.

## Consuming State in the UI

### BlocBuilder
Rebuilds the widget when state changes. Use the `buildWhen` parameter to filter unnecessary rebuilds.

```dart
BlocBuilder<AuthBloc, AuthState>(
  buildWhen: (previous, current) => previous != current,
  builder: (context, state) {
    return switch (state) {
      AuthInitial()        => const LoginForm(),
      AuthLoading()        => const CircularProgressIndicator(),
      AuthAuthenticated()  => HomePage(user: state.user),
      AuthFailure()        => ErrorView(message: state.message),
    };
  },
)
```

### BlocListener
Runs side effects (navigation, snackbars, dialogs) in response to state changes without rebuilding the widget tree.

```dart
BlocListener<AuthBloc, AuthState>(
  listenWhen: (previous, current) => current is AuthFailure,
  listener: (context, state) {
    if (state is AuthFailure) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.message)),
      );
    }
  },
  child: const LoginForm(),
)
```

### BlocConsumer
Combines `BlocBuilder` and `BlocListener` when you need both UI rebuilds and side effects.

```dart
BlocConsumer<AuthBloc, AuthState>(
  listenWhen: (_, current) => current is AuthAuthenticated || current is AuthFailure,
  listener: (context, state) {
    if (state is AuthAuthenticated) context.go('/home');
  },
  builder: (context, state) {
    return switch (state) {
      AuthLoading() => const CircularProgressIndicator(),
      _             => const LoginForm(),
    };
  },
)
```

**Rule:** Use `BlocListener` for side effects (navigation, toasts). Use `BlocBuilder` for UI. Never put `Navigator.push` or `ScaffoldMessenger` calls inside `builder`.

## Reading Blocs Without Rebuilding

Use `context.read<T>()` to dispatch events or call Cubit methods inside callbacks. Use `context.watch<T>()` only inside `build()` when you want the widget to rebuild on state changes (prefer `BlocBuilder` for clarity).

```dart
// Good — dispatching from a callback
ElevatedButton(
  onPressed: () => context.read<AuthBloc>().add(AuthLogoutRequested()),
  child: const Text('Log out'),
)

// Bad — context.watch inside build() is harder to scope than BlocBuilder
// Use BlocBuilder instead
```

## Testing

Test Blocs and Cubits with `bloc_test` — it provides a clean DSL for arranging state, acting, and asserting emitted states.

```dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AuthBloc', () {
    late AuthRepository mockRepository;

    setUp(() {
      mockRepository = FakeAuthRepository();
    });

    blocTest<AuthBloc, AuthState>(
      'emits [AuthLoading, AuthAuthenticated] on successful login',
      build: () => AuthBloc(authRepository: mockRepository),
      act: (bloc) => bloc.add(
        const AuthLoginRequested(email: 'a@b.com', password: 'pass'),
      ),
      expect: () => [
        isA<AuthLoading>(),
        isA<AuthAuthenticated>(),
      ],
    );

    blocTest<AuthBloc, AuthState>(
      'emits [AuthLoading, AuthFailure] on failed login',
      build: () => AuthBloc(authRepository: FakeFailingAuthRepository()),
      act: (bloc) => bloc.add(
        const AuthLoginRequested(email: 'bad@b.com', password: 'wrong'),
      ),
      expect: () => [isA<AuthLoading>(), isA<AuthFailure>()],
    );
  });
}
```

## Best Practices

- **Never put business logic in the UI.** The widget dispatches an event; the Bloc decides what to do.
- **Keep Blocs focused.** One Bloc per feature or domain concept. A `CartBloc` should not know about authentication.
- **States must be immutable.** Use `final` fields and `const` constructors. Use `copyWith` for partial updates.
- **One Bloc instance per subtree.** Don't create a new Bloc every time a page is pushed — provide it above the navigator or use `BlocProvider.value` to pass an existing instance down.
- **Close Blocs you create manually.** If you instantiate a Bloc outside of `BlocProvider`, call `bloc.close()` in `dispose()`. `BlocProvider` handles this automatically.
- **Use `Equatable` or override `==`** on state/event classes if you need value-based comparison in `buildWhen` / `listenWhen`. Without it, every new instance is considered a new state even if the data is identical.

```dart
// With Equatable
final class AuthAuthenticated extends AuthState with EquatableMixin {
  const AuthAuthenticated(this.user);
  final User user;

  @override
  List<Object?> get props => [user];
}
```

## Directory Placement

Bloc files live in the `presentation/providers/` directory of each feature (following the Flutter directory-structure convention), or in a dedicated `bloc/` subdirectory for larger features:

```
features/auth/
  presentation/
    bloc/                   # or providers/
      auth_bloc.dart        # Bloc class
      auth_event.dart       # sealed event hierarchy
      auth_state.dart       # sealed state hierarchy
    pages/
      login_page.dart
    widgets/
      login_form.dart
```
