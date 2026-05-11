# Safety Auditor Skill

When invoked to review code:

1. Scan the target files for `unsafe { ... }` blocks.
2. For each block, verify the presence of a `// SAFETY: ` comment. If missing, flag it.
3. Scan for `RefCell`, `Mutex`, and `RwLock`. 
4. Suggest architectural changes (e.g., message passing, restructuring lifetimes) that could eliminate the need for interior mutability.
5. Provide a summary report of findings and actionable refactoring steps.
