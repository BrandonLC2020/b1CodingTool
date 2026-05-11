---
name: call-claude-within-gemini
description: Execute tasks by spawning and delegating work to Claude Code. Use this when a task requires Claude Code's specific capabilities, or when requested to "use claude".
---

# Call Claude Code within Gemini CLI

This skill allows Gemini CLI to delegate tasks to Claude Code by executing it as a sub-process via the shell.

## Instructions

To call Claude Code, use your `run_shell_command` tool (or native bash equivalent) to execute the `claude` CLI. 
**Important Authentication Note:** To avoid conflicting with the user's default consumer subscription authentication, this skill uses a dedicated API key for automation managed via a `.env` file.

1. **Formulate the Prompt:** Create a clear, comprehensive prompt for Claude Code.
2. **Execute Claude Code:** Source the local `.env` file to load the automation keys, then use inline environment variable assignment to pass the API key.
   ```bash
   [ -f .env ] && source .env; ANTHROPIC_API_KEY="$CLAUDE_API_KEY_AUTOMATION" claude -p "Your comprehensive prompt here"
   ```
   *If the variable is not set, ask the user to provide their dedicated automation API key in the `.env` file.*
3. **Review Output:** Wait for the command to complete and review the output to ensure Claude successfully completed the task.
