# b1CodingTool: Phase 2 Implementation Plan

## Goal Description
Implement the core module definition schema and the `b1 install <module-name>` command. This phase establishes the mechanism for downloading and injecting community or tailored agent contexts, skills, and commands into a target project.

## Important Notes & Review Needed
> [!IMPORTANT]
> **API Details for skillsmp.com**: 
> The spec mentions connecting to `skillsmp.com` to parse and inject community skills. I noticed the site returns a Cloudflare block (403) or might not feature a public API endpoint yet. **Question:** Do you have an OpenAPI schema or example JSON format for the skillsmp.com endpoints? Alternatively, should I build a mocked HTTP fetcher that we can wire up properly later?
> 
> **Module Source & Hosting**: 
> For standard modules downloaded via `b1 install [module]`, are these hosted on a central b1 GitHub registry (like Homebrew), or fetched via the same skillsmp API? For Phase 2, I propose pointing our fetching logic to a configurable base URL or expecting a `.zip` / valid Git repository URI.

---

## Proposed Changes

### Module Schema
#### [NEW] `src/b1/core/schema.py`
Define the standard schema representing `module.yaml` (or `module.json`). The schema will include:
- `name` (str)
- `version` (str)
- `type` (Enum: cross_cutting, development, deployment)
- `dependencies` (list of other modules)
- Expected mappings for `skills/`, `commands/`, `hooks/`, and `context/`.

### Connection & Fetching Logic
#### [NEW] `src/b1/core/fetcher.py`
- Setup logic to hit the `skillsmp.com` API or a git endpoint.
- Utility to download, unpack, and validate the module's `module.yaml` against the schema.

### CLI Commands
#### [NEW] `src/b1/commands/install.py`
- Implement `b1 install <module_name>`.
- **UI:** Integrate Rich progress bars (e.g., `with Progress() as progress:`) to simulate/display the resolving, fetching, and unpacking stages.
- Mount the module folders into the target project's `.agent/modules/` directory.

#### [MODIFY] `src/b1/cli.py`
- Hook mapping for the new `install` parameter.

---

## Open Questions
> [!NOTE]
> 1. Should we add `httpx` and `pydantic` as dependencies to make data validation and fetching cleaner, or stick to standard library `urllib` and `json`?
> 2. For the downloaded modules, should they be copied directly into the project's folder, or centrally cached?

## Verification Plan
### Manual Verification
- We will mock a local module folder and run a mocked `uv run b1 install mock-module` to test scaffolding output and UI bars.
