# React Native (Expo): Directory Structure

## Expo Router File-Based Layout

Routes are discovered by filesystem layout under `app/`. The structure of `app/` **is** your navigation structure.

```
├── app.json                   # Expo config (plugins, splash screen, icons, etc.)
├── tsconfig.json
├── .env                       # Local secrets — never commit
├── app/                       # File-based routes (Expo Router)
│   ├── _layout.tsx            # Root layout — providers, global error boundary
│   ├── index.tsx              # "/" — app entry / home screen
│   ├── (auth)/                # Route group (no URL segment) — unauthenticated screens
│   │   ├── _layout.tsx        # Auth layout (e.g. no tab bar)
│   │   ├── login.tsx          # "/login"
│   │   └── register.tsx       # "/register"
│   └── (app)/                 # Route group — authenticated screens
│       ├── _layout.tsx        # Tab navigator or drawer lives here
│       ├── index.tsx          # Tab: Home
│       ├── profile/
│       │   ├── index.tsx      # "/profile"
│       │   └── [id].tsx       # "/profile/[id]" — dynamic segment
│       └── settings.tsx       # "/settings"
├── src/                       # All non-route source code
│   ├── core/                  # Shared, app-wide code
│   │   ├── components/        # Reusable UI primitives
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── index.ts
│   │   │   └── ...
│   │   ├── hooks/             # App-wide hooks (useDebounce, useAppState, etc.)
│   │   ├── theme/             # Design tokens, colors, spacing, typography
│   │   │   └── index.ts
│   │   ├── utils/             # Pure utility functions
│   │   └── constants/         # App-wide constants (API_BASE_URL, etc.)
│   └── features/
│       ├── auth/
│       │   ├── components/    # Feature-local UI components
│       │   ├── hooks/         # Feature-local hooks
│       │   ├── services/      # API calls for this feature
│       │   │   └── authService.ts
│       │   ├── store/         # State (Zustand store, etc.)
│       │   │   └── authStore.ts
│       │   └── types.ts
│       └── profile/
│           └── ...            # Same structure as auth/
├── assets/                    # Images, fonts, splash screens
└── __tests__/                 # (Optional) co-located tests are preferred
```

## Route Groups
Expo Router supports **route groups** (parenthesized directories like `(auth)`) that create layout boundaries without adding URL segments. Use them to:
- Apply different navigators (stack vs. tabs vs. drawer) to different sets of screens
- Gate authenticated vs. unauthenticated screens with a layout-level redirect

```tsx
// app/(app)/_layout.tsx — redirect unauthenticated users at the layout level
import { Redirect, Tabs } from 'expo-router';
import { useAuthStore } from '@/features/auth/store/authStore';

export default function AppLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Redirect href="/login" />;
  return <Tabs />;
}
```

## Feature Module Public API
Each feature exposes a public API via `index.ts`:

```ts
// src/features/auth/index.ts
export { useAuth } from './hooks/useAuth';
export { authService } from './services/authService';
export type { AuthUser } from './types';
```

Internal files (`store/`, `components/`) are implementation details — only import them within the feature.

## File Naming Rules
| Type | Convention | Example |
|------|-----------|---------|
| Route files | `kebab-case.tsx` | `user-profile.tsx` |
| Dynamic segments | `[param].tsx` | `[id].tsx` |
| Layouts | `_layout.tsx` | `_layout.tsx` |
| Components | `PascalCase.tsx` | `UserCard.tsx` |
| Hooks | `camelCase.ts` | `useAuth.ts` |
| Services | `camelCase.ts` | `authService.ts` |
| Tests | `<subject>.test.tsx` | `UserCard.test.tsx` |

## Key Config Files
| File | Purpose |
|------|---------|
| `app.json` | Expo project config — plugins, icons, splash, permissions |
| `tsconfig.json` | TypeScript config — set `paths` for `@/` alias pointing to `src/` |
| `.eslintrc.js` | Lint config — extend `expo` |
| `babel.config.js` | Babel config — required for Expo Router and Reanimated |
