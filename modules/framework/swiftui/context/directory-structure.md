# SwiftUI: Directory Structure

## Standard App Layout
```
Sources/
├── [AppName]App.swift      # Application entry point
├── Views/                  # Reusable UI components
│   ├── Common/             # Buttons, Text fields, etc.
│   └── Features/           # Feature-specific views
├── Models/                 # @Observable data models
├── ViewModels/             # (Optional) if using MVVM
└── Resources/              # Assets, Colors, Fonts
```

## Modular Structure
- **Domain-Specific Views:** Keep views co-located with the features they support.
- **Preview Assets:** Use `Preview Content` folder for mock JSON or images that should only be included in development builds.
