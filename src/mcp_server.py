"""MCP server – exposes all AI skills as MCP tools via FastMCP.

Run with:
    python -m src.mcp_server

or import and call ``create_server()`` to get a ``FastMCP`` instance.
"""

from __future__ import annotations

import os
import tempfile

from mcp.server.fastmcp import FastMCP

from src.skills import (
    CalculatorSkill,
    CodeExecutorSkill,
    FileManagerSkill,
    MemorySkill,
    WeatherSkill,
    WebSearchSkill,
)

# ---------------------------------------------------------------------------
# Skill instances (singletons shared across tool calls)
# ---------------------------------------------------------------------------

_calculator = CalculatorSkill()
_code_executor = CodeExecutorSkill()
_file_manager = FileManagerSkill(root=os.environ.get("MCP_FILES_ROOT", "./files"))
_memory = MemorySkill(
    store_path=os.environ.get("MCP_MEMORY_PATH", ".memory.json")
)
_weather = WeatherSkill()
_web_search = WebSearchSkill()


def create_server(name: str = "MCP-Agent-Skills") -> FastMCP:
    """Build and return the FastMCP server with all skills registered as tools."""

    mcp = FastMCP(
        name=name,
        instructions=(
            "An AI assistant with skills for calculation, code execution, "
            "file management, memory, weather lookup and web search."
        ),
    )

    # -----------------------------------------------------------------------
    # Tool: calculator
    # -----------------------------------------------------------------------

    @mcp.tool(description=CalculatorSkill.description)
    def calculator(expression: str) -> str:
        """Evaluate a mathematical expression and return the result."""
        return _calculator.run(expression)

    # -----------------------------------------------------------------------
    # Tool: code_executor
    # -----------------------------------------------------------------------

    @mcp.tool(description=CodeExecutorSkill.description)
    def code_executor(code: str, timeout: int = CodeExecutorSkill.DEFAULT_TIMEOUT) -> str:
        """Execute a Python code snippet and return stdout/stderr."""
        return _code_executor.run(code, timeout)

    # -----------------------------------------------------------------------
    # Tool: file_manager
    # -----------------------------------------------------------------------

    @mcp.tool(description=FileManagerSkill.description)
    def file_manager(action: str, path: str = "", content: str = "") -> str:
        """Perform file operations (read / write / list / delete)."""
        return _file_manager.run(action, path, content)

    # -----------------------------------------------------------------------
    # Tool: memory
    # -----------------------------------------------------------------------

    @mcp.tool(description=MemorySkill.description)
    def memory(action: str, key: str = "", value: str = "") -> str:
        """Persist and retrieve information (set / get / delete / list / clear)."""
        return _memory.run(action, key, value)

    # -----------------------------------------------------------------------
    # Tool: weather
    # -----------------------------------------------------------------------

    @mcp.tool(description=WeatherSkill.description)
    def weather(location: str) -> str:
        """Get the current weather for a location."""
        return _weather.run(location)

    # -----------------------------------------------------------------------
    # Tool: web_search
    # -----------------------------------------------------------------------

    @mcp.tool(description=WebSearchSkill.description)
    def web_search(query: str, max_results: int = 5) -> str:
        """Search the web using DuckDuckGo."""
        return _web_search.run(query, max_results)

    # -----------------------------------------------------------------------
    # Resource: skill catalogue
    # -----------------------------------------------------------------------

    @mcp.resource("skills://catalogue")
    def skill_catalogue() -> str:
        """List all available skills with their descriptions."""
        from src.skills import ALL_SKILLS

        lines = ["# Available Skills\n"]
        for skill_cls in ALL_SKILLS:
            lines.append(f"## {skill_cls.name}\n{skill_cls.description}\n")
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Prompt: agent task
    # -----------------------------------------------------------------------

    @mcp.prompt()
    def agent_task(task: str) -> str:
        """Return a system prompt that instructs the AI to complete *task* using the available tools."""
        return (
            "You are a capable AI agent with access to the following tools:\n"
            "- calculator: evaluate math expressions\n"
            "- code_executor: run Python code\n"
            "- file_manager: read/write/list/delete files\n"
            "- memory: store and retrieve information\n"
            "- weather: look up weather by location\n"
            "- web_search: search the web\n\n"
            f"Complete the following task step-by-step, using tools as needed:\n\n{task}"
        )

    return mcp


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    server = create_server()
    server.run()
