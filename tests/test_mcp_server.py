"""Tests for the MCP server – verify tools, resources and prompts are registered."""

import pytest

from src.mcp_server import create_server


class TestMCPServer:
    """Verify that the FastMCP server is built correctly."""

    @pytest.fixture(scope="class")
    def server(self, tmp_path_factory):
        import os

        root = tmp_path_factory.mktemp("files")
        mem_path = tmp_path_factory.mktemp("mem") / "memory.json"
        os.environ["MCP_FILES_ROOT"] = str(root)
        os.environ["MCP_MEMORY_PATH"] = str(mem_path)
        return create_server("test-server")

    def test_server_has_name(self, server):
        assert server.name == "test-server"

    def test_calculator_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "calculator" in tools

    def test_code_executor_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "code_executor" in tools

    def test_file_manager_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "file_manager" in tools

    def test_memory_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "memory" in tools

    def test_weather_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "weather" in tools

    def test_web_search_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "web_search" in tools

    def test_six_tools_total(self, server):
        tools = list(server._tool_manager.list_tools())
        assert len(tools) == 6

    @pytest.mark.asyncio
    async def test_calculator_tool_call(self, server):
        result = await server.call_tool("calculator", {"expression": "3 * 7"})
        # result is a list of content items; check that "21" appears somewhere
        text = " ".join(str(item) for item in result)
        assert "21" in text

    @pytest.mark.asyncio
    async def test_code_executor_tool_call(self, server):
        result = await server.call_tool("code_executor", {"code": "print('mcp')"})
        text = " ".join(str(item) for item in result)
        assert "mcp" in text

    @pytest.mark.asyncio
    async def test_memory_tool_set_get(self, server):
        await server.call_tool("memory", {"action": "set", "key": "x", "value": "99"})
        result = await server.call_tool("memory", {"action": "get", "key": "x"})
        text = " ".join(str(item) for item in result)
        assert "99" in text

    def test_skill_catalogue_resource_registered(self, server):
        resources = {r.uri for r in server._resource_manager.list_resources()}
        assert any("catalogue" in str(r) for r in resources)

    def test_agent_task_prompt_registered(self, server):
        prompts = {p.name for p in server._prompt_manager.list_prompts()}
        assert "agent_task" in prompts
