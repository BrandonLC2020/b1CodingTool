# Java: Directory Structure

## Standard Maven Layout
```
project_root/
├── pom.xml                # Maven configuration
├── src/
│   ├── main/
│   │   ├── java/          # Source code (package-structured)
│   │   └── resources/     # Config, static assets
│   └── test/
│       ├── java/          # Test suites (JUnit/TestNG)
│       └── resources/
└── target/                # Build artifacts (ignored)
```

## Standard Gradle Layout
```
project_root/
├── build.gradle           # Gradle configuration
├── src/                   # (Same layout as Maven)
└── build/                 # Build artifacts (ignored)
```
