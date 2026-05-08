import pytest
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from b1.server.mcp_server import mcp

@pytest.mark.asyncio
async def test_mcp_init(tmp_path):
    """Test the b1_init tool via MCP."""
    # FastMCP uses list_tools()
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "b1_init" in tool_names

@pytest.mark.asyncio
async def test_mcp_resources():
    """Test that MCP resources are registered."""
    resources = await mcp.list_resources()
    resource_uris = [str(r.uri) for r in resources]
    assert "b1://context/compiled" in resource_uris
    assert "b1://config/project" in resource_uris
    assert "b1://modules/library" in resource_uris

@pytest.mark.asyncio
async def test_b1_status_uninitialized(tmp_path, monkeypatch):
    """Test b1_status tool output when project is not initialized."""
    monkeypatch.chdir(tmp_path)
    # Call the underlying function directly for testing
    from b1.server.mcp_server import b1_status
    result = b1_status()
    assert "error" in result
    assert "Not a b1CodingTool project" in result
