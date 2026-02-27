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
    DataConverterSkill,
    DatetimeSkill,
    DiffToolSkill,
    FileManagerSkill,
    HashToolSkill,
    HttpRequestSkill,
    JsonProcessorSkill,
    MemorySkill,
    NoteTakerSkill,
    RandomGeneratorSkill,
    RegexToolSkill,
    ShellSkill,
    SystemInfoSkill,
    TaskListSkill,
    TextProcessorSkill,
    UnitConverterSkill,
    WeatherSkill,
    WebSearchSkill,
)

# ---------------------------------------------------------------------------
# Skill instances (singletons shared across tool calls)
# ---------------------------------------------------------------------------

_calculator = CalculatorSkill()
_code_executor = CodeExecutorSkill()
_data_converter = DataConverterSkill()
_datetime = DatetimeSkill()
_diff_tool = DiffToolSkill()
_file_manager = FileManagerSkill(root=os.environ.get("MCP_FILES_ROOT", "./files"))
_hash_tool = HashToolSkill()
_http_request = HttpRequestSkill()
_json_processor = JsonProcessorSkill()
_memory = MemorySkill(
    store_path=os.environ.get("MCP_MEMORY_PATH", ".memory.json")
)
_note_taker = NoteTakerSkill(
    store_path=os.environ.get("MCP_NOTES_PATH", ".notes.json")
)
_random_generator = RandomGeneratorSkill()
_regex_tool = RegexToolSkill()
_shell = ShellSkill()
_system_info = SystemInfoSkill()
_task_list = TaskListSkill(
    store_path=os.environ.get("MCP_TASKS_PATH", ".tasks.json")
)
_text_processor = TextProcessorSkill()
_unit_converter = UnitConverterSkill()
_weather = WeatherSkill()
_web_search = WebSearchSkill()


def create_server(name: str = "MCP-Agent-Skills") -> FastMCP:
    """Build and return the FastMCP server with all skills registered as tools."""

    mcp = FastMCP(
        name=name,
        instructions=(
            "An AI assistant with skills for calculation, code execution, "
            "data conversion, date/time handling, diffing, file management, "
            "hashing, HTTP requests, JSON processing, memory, note-taking, "
            "random generation, regex, shell commands, system info, task lists, "
            "text processing, unit conversion, weather lookup and web search."
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
    # Tool: data_converter
    # -----------------------------------------------------------------------

    @mcp.tool(description=DataConverterSkill.description)
    def data_converter(action: str, data: str = "", indent: int = 2) -> str:
        """Convert data between JSON, CSV, Base64, hex, and URL-encoding formats."""
        return _data_converter.run(action, data, indent)

    # -----------------------------------------------------------------------
    # Tool: datetime
    # -----------------------------------------------------------------------

    @mcp.tool(description=DatetimeSkill.description)
    def datetime(
        action: str,
        date: str = "",
        date2: str = "",
        fmt: str = "%Y-%m-%d %H:%M:%S",
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
    ) -> str:
        """Work with dates and times."""
        return _datetime.run(action, date, date2, fmt, days, hours, minutes)

    # -----------------------------------------------------------------------
    # Tool: diff_tool
    # -----------------------------------------------------------------------

    @mcp.tool(description=DiffToolSkill.description)
    def diff_tool(
        action: str = "unified",
        text_a: str = "",
        text_b: str = "",
        label_a: str = "text_a",
        label_b: str = "text_b",
        context_lines: int = 3,
    ) -> str:
        """Compare two texts and show their differences."""
        return _diff_tool.run(action, text_a, text_b, label_a, label_b, context_lines)

    # -----------------------------------------------------------------------
    # Tool: file_manager
    # -----------------------------------------------------------------------

    @mcp.tool(description=FileManagerSkill.description)
    def file_manager(action: str, path: str = "", content: str = "") -> str:
        """Perform file operations (read / write / list / delete)."""
        return _file_manager.run(action, path, content)

    # -----------------------------------------------------------------------
    # Tool: hash_tool
    # -----------------------------------------------------------------------

    @mcp.tool(description=HashToolSkill.description)
    def hash_tool(
        action: str, text: str = "", secret: str = "", encoding: str = "utf-8"
    ) -> str:
        """Hash text using MD5, SHA-256, BLAKE2b, HMAC and other algorithms."""
        return _hash_tool.run(action, text, secret, encoding)

    # -----------------------------------------------------------------------
    # Tool: http_request
    # -----------------------------------------------------------------------

    @mcp.tool(description=HttpRequestSkill.description)
    def http_request(
        action: str,
        url: str,
        body: str = "",
        headers: str = "",
        timeout: int = HttpRequestSkill._DEFAULT_TIMEOUT,
    ) -> str:
        """Make HTTP GET, POST or HEAD requests to external URLs."""
        return _http_request.run(action, url, body, headers, timeout)

    # -----------------------------------------------------------------------
    # Tool: json_processor
    # -----------------------------------------------------------------------

    @mcp.tool(description=JsonProcessorSkill.description)
    def json_processor(
        action: str, data: str = "", path: str = "", value: str = ""
    ) -> str:
        """Parse, query and manipulate JSON data using dot-notation paths."""
        return _json_processor.run(action, data, path, value)

    # -----------------------------------------------------------------------
    # Tool: memory
    # -----------------------------------------------------------------------

    @mcp.tool(description=MemorySkill.description)
    def memory(action: str, key: str = "", value: str = "") -> str:
        """Persist and retrieve information (set / get / delete / list / clear)."""
        return _memory.run(action, key, value)

    # -----------------------------------------------------------------------
    # Tool: note_taker
    # -----------------------------------------------------------------------

    @mcp.tool(description=NoteTakerSkill.description)
    def note_taker(
        action: str,
        title: str = "",
        content: str = "",
        note_id: int = 0,
        tags: str = "",
        query: str = "",
    ) -> str:
        """Create and manage structured notes with titles, content and tags."""
        return _note_taker.run(action, title, content, note_id, tags, query)

    # -----------------------------------------------------------------------
    # Tool: random_generator
    # -----------------------------------------------------------------------

    @mcp.tool(description=RandomGeneratorSkill.description)
    def random_generator(
        action: str,
        length: int = 16,
        min_val: float = 0,
        max_val: float = 100,
        items: str = "",
        include_symbols: bool = True,
    ) -> str:
        """Generate UUIDs, passwords, hex tokens, random numbers and more."""
        return _random_generator.run(action, length, min_val, max_val, items, include_symbols)

    # -----------------------------------------------------------------------
    # Tool: regex_tool
    # -----------------------------------------------------------------------

    @mcp.tool(description=RegexToolSkill.description)
    def regex_tool(
        action: str,
        pattern: str,
        text: str = "",
        replacement: str = "",
        flags: str = "",
    ) -> str:
        """Test and apply regular expressions (match, search, findall, replace, split)."""
        return _regex_tool.run(action, pattern, text, replacement, flags)

    # -----------------------------------------------------------------------
    # Tool: shell
    # -----------------------------------------------------------------------

    @mcp.tool(description=ShellSkill.description)
    def shell(
        command: str,
        timeout: int = ShellSkill.DEFAULT_TIMEOUT,
        cwd: str = "",
    ) -> str:
        """Execute a shell command and return its output."""
        return _shell.run(command, timeout, cwd)

    # -----------------------------------------------------------------------
    # Tool: system_info
    # -----------------------------------------------------------------------

    @mcp.tool(description=SystemInfoSkill.description)
    def system_info(action: str = "all") -> str:
        """Retrieve OS, Python runtime, environment, and working directory info."""
        return _system_info.run(action)

    # -----------------------------------------------------------------------
    # Tool: task_list
    # -----------------------------------------------------------------------

    @mcp.tool(description=TaskListSkill.description)
    def task_list(action: str, title: str = "", task_id: int = 0) -> str:
        """Manage a persistent to-do task list."""
        return _task_list.run(action, title, task_id)

    # -----------------------------------------------------------------------
    # Tool: text_processor
    # -----------------------------------------------------------------------

    @mcp.tool(description=TextProcessorSkill.description)
    def text_processor(
        action: str,
        text: str = "",
        find: str = "",
        replace_with: str = "",
        max_length: int = 100,
        separator: str = "\n",
        count: int = 2,
    ) -> str:
        """Manipulate and analyse text (case, count, replace, split, trim, etc.)."""
        return _text_processor.run(action, text, find, replace_with, max_length, separator, count)

    # -----------------------------------------------------------------------
    # Tool: unit_converter
    # -----------------------------------------------------------------------

    @mcp.tool(description=UnitConverterSkill.description)
    def unit_converter(
        category: str, value: float, from_unit: str, to_unit: str
    ) -> str:
        """Convert between length, weight, temperature, volume, speed and area units."""
        return _unit_converter.run(category, value, from_unit, to_unit)

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
            "- data_converter: convert between JSON/CSV/Base64/hex/URL formats\n"
            "- datetime: work with dates and times\n"
            "- diff_tool: compare two texts and show differences\n"
            "- file_manager: read/write/list/delete files\n"
            "- hash_tool: hash text with MD5/SHA/BLAKE2b/HMAC\n"
            "- http_request: make HTTP GET/POST/HEAD requests\n"
            "- json_processor: parse/query/manipulate JSON data\n"
            "- memory: store and retrieve key-value information\n"
            "- note_taker: create and search structured notes\n"
            "- random_generator: generate UUIDs, passwords, random numbers\n"
            "- regex_tool: test and apply regular expressions\n"
            "- shell: execute shell commands\n"
            "- system_info: retrieve OS and runtime information\n"
            "- task_list: manage a to-do task list\n"
            "- text_processor: manipulate and analyse text\n"
            "- unit_converter: convert between measurement units\n"
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
