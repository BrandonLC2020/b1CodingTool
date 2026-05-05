# Flutter: Commands

These commands are recommended for agents to assist in Flutter development workflows.

## Feature Commands
- **/setup-flutter-bloc**: Scaffold a new BLoC/Cubit for a feature, including state, event, and bloc files following the feature-first directory structure.
- **/gen-models**: Run `build_runner` to generate `.g.dart` or `.freezed.dart` files.

## Integration with b1
- `b1 install flutter`: Installs guidelines and triggers a `flutter pub get` via post-install hook.
- `b1 pair`: Synchronizes Flutter-specific BLoC and logging standards across all agent context files.
