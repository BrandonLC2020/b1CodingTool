# TypeScript: Dependency Management

## Package Managers
- **pnpm (Recommended):** Fast, disk-efficient, and great for monorepos.
- **npm:** Universal compatibility.
- **Yarn:** Mature ecosystem.

## Common Commands (pnpm)
```bash
pnpm init                  # Initialize project
pnpm add <package>         # Add runtime dependency
pnpm add -D <package>      # Add dev dependency (including @types)
pnpm install               # Install from lockfile
pnpm run <script>          # Run a package.json script
```

## Type Definitions
Always install `@types/<package>` for libraries that do not ship with built-in type definitions.
