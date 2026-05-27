# GitHub Bots: Best Practices

## Identity
- **Prefer GitHub Apps over PATs.** Apps have scoped permissions, installation tokens that expire, and clear audit-log attribution.
- **Never run bots as a real user's PAT.** When the user leaves, every bot they ran silently breaks — and their personal access traces every automated action.
- **Give each bot its own GitHub App.** One app per responsibility: `release-bot`, `triage-bot`, `dependency-bot`. Don't grant a single app the union of all needed permissions.

## Permissions
- **Start from zero scopes and add only what's needed.** A labeler bot needs `issues: write` and `pull-requests: write` — nothing more.
- **Restrict app installation to the repos that need it.** Org-wide installation should be rare and reviewed.

## Audit
- Tag all bot-authored commits/PRs with a label (`bot:<name>`) so they are filterable.
- Review the org audit log quarterly for unexpected bot activity.

## Failure Modes
- **Set bot workflows to fail loudly.** A silently broken dependabot is worse than no dependabot — it gives false assurance.
- **Test bot changes in a fork or non-default branch first.** A misconfigured labeler can spam every open issue.
