# Design Doc: link-to-clickup-list Command

## Overview
The `link-to-clickup-list` command allows users to link a `b1` project to a specific ClickUp list. This connection is persisted in the project's local configuration, enabling the agent to autonomously identify the target list for task management without user intervention.

## Problem Statement
Currently, the `b1` agent has to either infer the destination ClickUp list or ask the user for it when creating tasks. This slows down the developer experience and can lead to tasks being created in the wrong location.

## Success Criteria
- Users can run `b1 link-to-clickup-list <url_or_id>`.
- The command supports both full ClickUp list URLs and raw list IDs.
- The command verifies the list exists using the ClickUp MCP before saving.
- The list ID is persisted in `.agent/config.yaml`.
- Future agent operations can read this ID from the configuration.

## Architecture

### 1. Configuration Schema (`src/b1/core/config.py`)
Add a new optional field `clickup_list_id` to the `B1Config` Pydantic model.

### 2. Command Logic (`src/b1/commands/link_clickup.py`)
- **Extraction:** A utility function or regex to parse the list ID from the input string.
- **Verification:** Use the `getListInfo` tool from the ClickUp MCP.
- **Update:** Update the `B1Config` and save it to the filesystem.

### 3. CLI Entry Point (`src/b1/cli.py`)
Register the command with Typer.

## Implementation Details

### List ID Extraction
Regex: `(?:li\/|)(\d{11,13})`
- Matches `901414778471`
- Matches `https://app.clickup.com/90141049639/v/li/901414778471`

### Flow
1. Receive input string.
2. Extract ID using regex.
3. If no ID found, exit with error.
4. Call `getListInfo(list_id=extracted_id)`.
5. If list info retrieved:
   - Load `B1Config`.
   - Set `config.clickup_list_id = extracted_id`.
   - `config.save(Path.cwd())`.
   - Print success message with list name.
6. If list info fails, print error message and exit.

## Testing Plan

### Unit Tests (`tests/unit/test_link_clickup.py`)
- Test extraction logic with various ClickUp URL formats.
- Test extraction logic with raw IDs.
- Test extraction logic with invalid inputs.

### Integration Tests (`tests/integration/test_link_clickup_cmd.py`)
- Mock the ClickUp MCP response.
- Verify that running the command updates the `.agent/config.yaml` file correctly.
- Verify error handling when not in a `b1` project.
