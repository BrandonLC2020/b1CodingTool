# b1CodingTool: Phase 5 Implementation Plan

## Goal Description
Implement the `b1 dashboard` execution environment. This encompasses standing up a local FastAPI backend strictly responsible for translating `.agent` configurations and API calls, paired directly with a gorgeous, high-fidelity React Single Page Application (SPA). The dashboard will monitor installed modules, catalog skills, securely proxy keys, and show live telemetry.

## Important Notes & Review Needed
> [!IMPORTANT]
> **Frontend Bundler**:
> Based on your global agent rule set, it is recommended to build modern, highly aesthetic UIs using Vite for React and Vanilla CSS. Are you comfortable with `vite` scaffolding the dashboard folder natively inside this repo, or would you prefer Next.js?
>
> **Styling**:
> I am instructed to avoid TailwindCSS unless you specifically authorize it. I will build an extremely premium, dark-mode focused UI using pure Vanilla CSS. If you'd rather pivot to Tailwind CSS, please explicitly say so!
>
> **Serving the SPA**:
> In production environments (when using a CLI tool), the React app is usually compiled down into a `dist/` folder and `FastAPI` is configured to serve those static HTML files via `127.0.0.1:8000`. Is this the correct intended architecture? 

---

## Proposed Changes

### Backend Control Plane
#### [NEW] `src/b1/server/main.py`
- Expose a `FastAPI` instance.
- Develop core REST routing connecting directly to our existing parsers (`B1Config`, `ModuleFetcher`, `ContextCompiler`).
- **Endpoints**:
  - `GET /api/modules` - returns mapped modules inside `.agent/modules`
  - `GET /api/config` - returns the current parity and upstream state.
  - `POST /api/modules/install` - equivalent to `b1 install`

#### [MODIFY] `src/b1/commands/dashboard.py` (and `cli.py`)
- Implement `b1 dashboard`.
- The Typer process will bind to `uvicorn` and spin up the `FastAPI` app.

### Frontend Application
#### [NEW] `dashboard/`
- Standard `vite` React scaffolding utilizing TypeScript.
- Implementation of the Core Views defined in the specification:
  - **Module Explorer**
  - **Skill Inspector**
  - **Resource Manager**
  - **Telemetry Dashboard**

## Open Questions
> [!NOTE]
> Since we do not have an LLM metrics system actively integrated right now (just the foundations), the **Telemetry** view might need to be stubbed with mock data. Are there specific logs or API proxies already being tracked on your system that I should hook into, or is mocking fine for Phase 5 scaffolding?

## Verification Plan
### Local Dev Check
- Make sure `uv run b1 dashboard` correctly binds `FastAPI`.
- Verify the Vite server can boot up locally and hit the `/api` namespaces successfully bridging the Python-React gap.
