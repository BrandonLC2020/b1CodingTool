# General: Best Practices

## Project Management
- **Modular Growth:** Build features in small, independent modules. Avoid monolithic structures.
- **Documentation First:** Document architectural decisions and API designs before implementation.
- **Continuous Validation:** Run tests and linters frequently during development, not just before a commit.

## Code Quality
- **KISS (Keep It Simple, Stupid):** Prioritize readability and simplicity over clever or highly abstracted code.
- **DRY (Don't Repeat Yourself):** Extract common logic into reusable utilities or components, but avoid premature abstraction.
- **Error Handling:** Anticipate failures and handle them gracefully with descriptive error messages.

## Agent Collaboration
- **Clear Intent:** When using an agent, provide specific, high-level objectives.
- **Context Management:** Use ignore files (`.gitignore`, `.geminiignore`, etc.) to keep the agent's context window focused on relevant files.
- **Review Always:** Always review agent-generated code for security, performance, and stylistic consistency.
