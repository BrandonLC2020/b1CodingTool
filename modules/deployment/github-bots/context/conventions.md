# GitHub Bots: Conventions

## File Layout
```
.github/
├── dependabot.yml                # Dependabot ecosystem config
├── labeler.yml                   # actions/labeler path rules
└── workflows/
    ├── release-please.yml        # googleapis/release-please-action
    └── triage-labeler.yml        # actions/labeler workflow
```

## Label Taxonomy
- **Type:** `type:bug`, `type:feature`, `type:docs`, `type:refactor`
- **Area:** `area:cli`, `area:server`, `area:dashboard`, `area:modules`
- **Bot:** `bot:dependabot`, `bot:release-please`, `bot:triage`

## Dependabot Cadence
- Critical ecosystems (npm, pip with security advisories): `weekly`.
- Slower-moving ecosystems (docker base images, github-actions): `monthly`.
- Group patch-level updates to reduce PR noise: `groups:` with `update-types: [patch]`.

## Release-Please
- Use conventional commits (`feat:`, `fix:`, `chore:`) to drive version bumps.
- Pin `release-please-action` to a specific commit SHA, not a tag.
