# TypeScript: Coding Conventions

## Style Guide
- **Consistency:** Use **ESLint** and **Prettier**. Follow the airbnb or standard-ts guidelines.
- **Indentation:** Use 2 spaces for web projects, 2 or 4 for Node.js projects (be consistent).
- **Line Length:** Typically 80 or 100 characters.

## Naming
| Entity | Convention | Example |
|--------|-----------|---------|
| Files | `PascalCase.ts` (classes), `camelCase.ts` (utils/hooks) | `UserService.ts`, `useAuth.ts` |
| Interfaces / Types | `PascalCase` | `UserRecord`, `AuthResponse` |
| Classes | `PascalCase` | `APIClient`, `Validator` |
| Functions / Methods | `camelCase` | `fetchData()`, `validateInput()` |
| Variables | `camelCase` | `userCount`, `isActive` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES`, `BASE_URL` |

## Documentation
- **TSDoc:** Use JSDoc-style comments with TSDoc tags (e.g., `@param`, `@returns`, `@throws`) for all public APIs.
