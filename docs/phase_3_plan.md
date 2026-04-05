# b1CodingTool: Phase 3 Implementation Plan

## Goal Description
Implement `b1 pull` and `b1 push` commands. `b1 pull` will iterate installed modules and update them from their upstream sources. `b1 push` will provide a mechanism to scan local project adjustments and automate Pull Request creation towards a central repository.

## Important Notes & Review Needed
> [!IMPORTANT]
> **Pushing Details (`b1 push`)**: 
> 1. To automatically draft a Pull Request, do you want to rely on the user having the GitHub CLI (`gh`) installed, or should I attempt to build API calls requiring the user to configure a GitHub PAT? Using `gh pr create` is much easier if users have it.
> 2. What triggers a "scan"? Should `b1 push` read through `.agent/project/agent.md` and do an LLM evaluation (using an LLM provider) to extract "generalized learnings", or simply push the entire raw file up to the central repository for human review?
> 3. Does the system need a `b1config.yaml` at the root project to track the central "upstream" repository URL?

---

## Proposed Changes

### Configuration
#### [NEW] `src/b1/core/config.py`
- Expose handling for an optional `.agent/config.yaml` to store the target `upstream_repo` for PR automation.

### Pull Logic (`b1 pull`)
#### [NEW] `src/b1/commands/pull.py`
#### [MODIFY] `src/b1/cli.py` (Add `pull` command)
- Scan `./.agent/modules/` directories for installed modules.
- Re-trigger `ModuleFetcher` against the cached sources in `~/.b1/cache` to execute `git pull origin main`.
- Use the `ModuleInstaller` to silently overwrite/update the local project's module files.

### Push Logic (`b1 push`)
#### [NEW] `src/b1/commands/push.py`
#### [MODIFY] `src/b1/cli.py` (Add `push` command)
- Create a temporary tracking branch for `.agent/project/agent.md` (or specific skills).
- Formulate a command to `gh pr create --title "..." --body "..."` or print out a deep-link URL that opens the browser to explicitly draft the PR.

## Open Questions
> [!NOTE]
> Do you want `b1 pull` to also trigger the shell `install_command` arrays defined in the module's skills again (e.g., essentially running `npm install` again), or just sync the raw text files?

## Verification Plan
### Manual Testing
- Add `mock-module` back. Update it locally in the cache to simulate an upstream update.
- Run `b1 pull` and assert the files change.
- Run `b1 push` and ensure it creates the branch and correctly formats a PR (or PR creation link).
