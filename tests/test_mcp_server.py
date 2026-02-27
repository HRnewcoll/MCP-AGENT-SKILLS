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

    def test_twenty_tools_total(self, server):
        tools = list(server._tool_manager.list_tools())
        assert len(tools) == 20

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

    # New tool registration tests

    def test_data_converter_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "data_converter" in tools

    def test_datetime_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "datetime" in tools

    def test_diff_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "diff_tool" in tools

    def test_hash_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "hash_tool" in tools

    def test_http_request_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "http_request" in tools

    def test_json_processor_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "json_processor" in tools

    def test_note_taker_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "note_taker" in tools

    def test_random_generator_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "random_generator" in tools

    def test_regex_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "regex_tool" in tools

    def test_shell_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "shell" in tools

    def test_system_info_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "system_info" in tools

    def test_task_list_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "task_list" in tools

    def test_text_processor_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "text_processor" in tools

    def test_unit_converter_tool_registered(self, server):
        tools = {t.name for t in server._tool_manager.list_tools()}
        assert "unit_converter" in tools

    @pytest.mark.asyncio
    async def test_datetime_tool_call(self, server):
        result = await server.call_tool("datetime", {"action": "now"})
        text = " ".join(str(item) for item in result)
        assert "UTC" in text

    @pytest.mark.asyncio
    async def test_hash_tool_call(self, server):
        result = await server.call_tool("hash_tool", {"action": "sha256", "text": "hello"})
        text = " ".join(str(item) for item in result)
        assert "2cf24dba" in text

    @pytest.mark.asyncio
    async def test_text_processor_tool_call(self, server):
        result = await server.call_tool(
            "text_processor", {"action": "uppercase", "text": "hello"}
        )
        text = " ".join(str(item) for item in result)
        assert "HELLO" in text

    @pytest.mark.asyncio
    async def test_unit_converter_tool_call(self, server):
        result = await server.call_tool(
            "unit_converter",
            {"category": "length", "value": 1.0, "from_unit": "km", "to_unit": "m"},
        )
        text = " ".join(str(item) for item in result)
        assert "1000" in text

    @pytest.mark.asyncio
    async def test_random_generator_uuid(self, server):
        import re
        result = await server.call_tool("random_generator", {"action": "uuid"})
        text = " ".join(str(item) for item in result)
        assert re.search(r"[0-9a-f\-]{36}", text)

    @pytest.mark.asyncio
    async def test_task_list_add_list(self, server):
        await server.call_tool("task_list", {"action": "add", "title": "MCP task"})
        result = await server.call_tool("task_list", {"action": "list"})
        text = " ".join(str(item) for item in result)
        assert "MCP task" in text
