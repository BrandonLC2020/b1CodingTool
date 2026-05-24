# Git Collaboration Templates

Use repo-provided templates first. These are fallbacks when no project-specific template exists.

## Commit messages

### Small change

```text
fix(parser): handle empty config files

Return the default config when the parser receives an empty file instead of
raising an uncaught exception.

Tests: npm test -- parser
Fixes #123
```

### Documentation change

```text
docs: add troubleshooting steps for local setup

Document the missing dependency error and the command that resolves it so new
contributors can complete setup without searching old issues.

Tests: not run (docs-only change)
Refs: #456
```

### Breaking change

```text
feat(api): require explicit pagination limit

Require clients to pass a page limit so large exports cannot accidentally load
unbounded result sets.

BREAKING CHANGE: API clients must pass `limit` on list endpoints.
Migration: set `limit=100` to preserve the previous default behavior.

Tests: pytest tests/api/test_pagination.py
```

## Pull request / merge request

```markdown
## Summary
- 
- 
- 

## Motivation / context
Closes #

## Testing
- [ ] `<command>`

## Risk and impact
- Risk level: low / medium / high
- User/operator impact:
- Rollback plan:

## Review notes
- 

## Screenshots / logs
<!-- Add when UI, CLI, dashboards, or error output changed. -->
```

## Bug issue

```markdown
## Summary

## Steps to reproduce
1. 
2. 
3. 

## Expected behavior

## Actual behavior

## Environment
- OS:
- Version / commit:
- Configuration:

## Logs / screenshots

## Acceptance criteria
- [ ] 
```

## Feature issue

```markdown
## Summary

## Problem / user need

## Proposed behavior

## Alternatives considered

## Constraints / non-goals

## Acceptance criteria
- [ ] 
- [ ] Tests/docs updated if needed
```

## Code review comment

```markdown
suggestion: Could we validate `<condition>` before calling `<function>`?

If `<condition>` is false, this path can return `<bad outcome>`. A small guard
here would make the failure mode explicit and easier to test.
```

## Discussion post

```markdown
## Context

## Proposal / question

## Options considered
1. 
2. 
3. 

## Trade-offs

## Recommendation

## Next steps
- [ ] 
```

## Release note

```markdown
### Fixed
- Fixed `<user-visible problem>` when `<condition>` occurs. (#123)

### Changed
- Changed `<behavior>` to `<new behavior>`. Operators should `<migration step>`.

### Security
- Hardened `<area>` against `<risk>`. Users should upgrade promptly.
```
