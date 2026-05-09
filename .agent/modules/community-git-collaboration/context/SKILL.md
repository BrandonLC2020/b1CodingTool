---
name: git-collaboration
description: Git collaboration playbook for agents. Use when performing or advising on git operations, drafting commits, branch names, PR/MR descriptions, issue reports, code review comments, release notes, changelog entries, or GitHub/GitLab discussion posts.
---

# Git Collaboration

Use this skill whenever the user asks for git/GitHub/GitLab help, or when your task may create commits, branches, PRs, issues, review comments, or public-facing project discussion text.

## Non-negotiable safety rules

1. **Protect user work.** Run `git status --short --branch` before mutating git state. Do not overwrite, reset, clean, rebase, amend, squash, or force-push changes you did not create unless the user explicitly asks.
2. **Inspect before acting.** Prefer read-only commands first: `git status`, `git diff`, `git diff --staged`, `git log --oneline --decorate -n 20`, `git branch --show-current`, `git remote -v`.
3. **Ask before external side effects.** Get explicit approval before pushing, opening/closing PRs or issues, posting comments, changing labels/milestones, deleting branches, or publishing releases.
4. **Never include secrets.** Check staged diffs for tokens, credentials, local paths, private data, debug dumps, and generated artifacts before committing or posting.
5. **Respect repo conventions first.** Look for `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `.github/PULL_REQUEST_TEMPLATE*`, `.github/ISSUE_TEMPLATE/`, `docs/`, changelog policy, branch protection, commitlint, or release tooling before inventing a format.
6. **Do not bypass safeguards.** Never skip hooks with `--no-verify`, bypass signing with `--no-gpg-sign`, or use destructive broad commands unless the user explicitly asks after seeing what will be lost.

## Agent workflow for git tasks

1. **Clarify intent**: determine whether the user wants advice, local changes only, a commit, a PR/MR draft, an issue, or an actual remote action.
2. **Survey repo state**:
   - current branch and upstream
   - clean/dirty status
   - untracked files
   - staged vs unstaged changes
   - existing templates and contribution rules
3. **Plan atomic work**: keep unrelated changes separate; propose multiple commits/PRs if the diff mixes concerns.
4. **Before committing**:
   - review `git diff` and `git diff --staged`
   - stage only intended files/hunks
   - run relevant tests/linters or explain why not run
   - write the message in a temp file for multi-line commits when possible
5. **Before posting/pushing**:
   - summarize what will be published
   - confirm target remote/branch/base branch
   - ask for approval unless the user already gave explicit permission
6. **Final response**: report changed files, commit hash if created, tests run, and any follow-up action needed.

## Commit best practices

Prefer the repository's existing style. If none is obvious, use a conventional, concise, imperative style.

### Commit title

- Aim for **50 characters**; hard cap around **72 characters**.
- Use imperative mood: `Add`, `Fix`, `Remove`, `Refactor`, `Document`.
- State the user-visible change, not the implementation chore.
- Add a scope when useful: `docs: clarify PR template`, `feat(api): add pagination`.
- Avoid vague titles: `updates`, `fix stuff`, `work in progress`, `misc`.

### Commit body

Include a body when the change is non-trivial:

```text
<type>(<scope>): <imperative summary>

Explain why this change is needed and what changed at a high level.
Mention trade-offs, compatibility, migrations, or follow-up work.

Tests: <commands run, or "not run (<reason>)">
Refs: #123
```

Guidelines:

- Wrap body lines near 72 characters.
- Explain **why**, not just what the diff already shows.
- Reference issues with `Fixes #123`, `Closes #123`, or `Refs #123` only when appropriate.
- Use trailers consistently: `Co-authored-by: Name <email>`, `Signed-off-by:`, `BREAKING CHANGE:`.
- Do not claim tests passed unless they were run in this session or clearly provided by the user/CI.
- Prefer new commits over amending after hook failures. A failed hook means the attempted commit did not happen; `git commit --amend` would modify the previous commit.
- Stage specific files or hunks by name. Avoid `git add -A` and `git add .` unless the user explicitly wants every tracked and untracked change included.

## Branch naming

Use repo conventions first. Otherwise prefer:

- `feature/<short-topic>` for new capability
- `fix/<short-topic>` for bugs
- `docs/<short-topic>` for documentation
- `refactor/<short-topic>` for behavior-preserving restructuring
- `chore/<short-topic>` for maintenance
- Include issue id when useful: `fix/123-handle-empty-cache`

Keep branch names lowercase, hyphenated, short, and descriptive.

## PR/MR best practices

Before drafting, inspect the diff and existing PR template. A good PR makes review easy.

Include:

1. **Summary**: 2-4 bullets of what changed.
2. **Motivation/context**: why this is needed; link issues/discussions.
3. **Testing**: exact commands and results, or why tests were not run.
4. **Risk/impact**: migrations, compatibility, performance, security, UX, docs.
5. **Review notes**: files/areas that deserve attention; known limitations.
6. **Screenshots/logs** when UI, CLI output, dashboards, or errors changed.
7. **Rollback plan** for risky production changes when applicable.

PR title should be review-friendly and usually match the main commit title. Avoid overloading one PR with unrelated work; suggest splitting if needed.

## Merge strategy

- Rebase local feature branches before opening a PR when the repo expects linear history.
- Prefer merge commits or squash merges for PRs when that is the repository norm.
- Never rebase commits that other people may have based work on.
- Delete merged branches promptly when branch ownership is clear.
- Use `git worktree add ../project-feature feature/my-feature` when parallel work needs separate working directories.

## Issue best practices

Use existing issue templates first. Otherwise structure issues as:

```markdown
## Summary
One or two sentences describing the problem or request.

## Context
Why this matters, who is affected, links to prior work.

## Steps to reproduce
1. ...
2. ...
3. ...

## Expected behavior
...

## Actual behavior
...

## Environment
OS, versions, commit SHA, config, logs, screenshots as relevant.

## Acceptance criteria
- [ ] Observable condition for done
- [ ] Tests/docs/compatibility expectations
```

For feature requests, replace reproduction with use cases, constraints, alternatives considered, and clear acceptance criteria.

## Review comments and discussion posts

Write comments that are specific, kind, and actionable.

- Start with the concrete observation and its impact.
- Distinguish blockers from nits/preferences.
- Suggest a fix or ask a focused question.
- Cite files, lines, docs, tests, or prior decisions when possible.
- Prefer "Could we..." / "Would it be safer to..." over blame-oriented language.
- Summarize decisions and next steps at the end of long threads.
- Do not post speculative claims as facts; label uncertainty.

Useful prefixes:

- `blocking:` must be addressed before merge
- `suggestion:` optional improvement
- `question:` clarification request
- `nit:` minor style/readability point
- `praise:` call out something done well

## Release notes and changelog entries

Write for users, not only maintainers.

- Group by `Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`, `Security` when possible.
- Mention migration steps and breaking changes clearly.
- Credit contributors according to repo policy.
- Avoid internal-only implementation details unless they affect users/operators.

## Reference templates

For copy-ready examples, see [references/templates.md](references/templates.md).
