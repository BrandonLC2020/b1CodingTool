# TypeScript: Directory Structure

## Standard Node.js Structure
```
project_root/
├── tsconfig.json          # TypeScript configuration
├── package.json
├── src/                   # Source code
│   ├── index.ts           # Entry point
│   ├── core/              # Shared logic
│   ├── features/          # Feature-based organization
│   └── types/             # Shared interfaces/types
├── tests/                 # Vitest or Jest suites
│   ├── unit/
│   └── integration/
└── dist/                  # Compiled JS output (ignored)
```

## Barrel Exports
Use `index.ts` files to define the public API of a directory and simplify imports.
