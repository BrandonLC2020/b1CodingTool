# B1 Pair Context Refactoring Design

## Summary
The `b1 pair` command currently generates monolithic `CLAUDE.md`, `GEMINI.md`, and `CODEX.md` files containing the entirety of the root, project, and module contexts. This causes massive context bloat for the agents. This design shifts the output to generate lightweight root files acting as a "filemap", while generating per-agent formatted context files inside hidden folders (`.claude/`, `.gemini/`, `.codex/`).

## Architecture

1. **Context Parsing**: 
   The `AgentTranslator` will continue to parse the compiled context string into sections (e.g., "Root Context", "Project Context", "Module Context [module_name]").

2. **Hidden Folders and Per-Agent Files**:
   For each target agent, `b1 pair` will create a corresponding hidden directory in the project root:
   - `CLAUDE` -> `.claude/`
   - `GEMINI` -> `.gemini/`
   - `CODEX` -> `.codex/`
   
   Inside these directories, individual context files will be generated for each parsed section (e.g., `.claude/root_context.md`). These files will be formatted using the specific syntax for that agent (e.g., XML tags for Claude).

3. **Root Filemap (CLAUDE.md, GEMINI.md, etc.)**:
   The root agent instruction files will be replaced with lightweight index files. These files will contain:
   - A brief instruction telling the agent to read the mapped files only when relevant context is needed.
   - A bulleted list of paths pointing to the files in the hidden directories.

## Components to Modify

- `src/b1/core/translator.py`:
  - Update `generate_files` to create the hidden directory (`.{agent.lower()}/`).
  - Update the per-agent format methods (`_format_claude`, `_format_gemini`, etc.) or change the flow to write individual files to the hidden directory instead of a single string.
  - Implement a new method to generate the root filemap string and write it to `{AGENT}.md`.

## Error Handling & Edge Cases
- Ensure the hidden directories are created if they do not exist (`os.makedirs(exist_ok=True)`).
- Clean up old files in the hidden directory if contexts are removed? (Preferably yes, to avoid stale context files. Wiping the directory before generation is a good idea).
- Ensure file paths in the root map are relative to the project root.
