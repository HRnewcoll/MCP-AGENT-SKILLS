# MCP-AGENT-SKILLS

A Python implementation of **Model Context Protocol (MCP) skills** and an **agentic loop** for AI assistants — inspired by how Claude / ClaudeBot approaches tool use.

---

## What's inside

| Module | Description |
|--------|-------------|
| `src/mcp_server.py` | FastMCP server that exposes every skill as an MCP **tool**, plus a resource catalogue and a prompt template |
| `src/agent.py` | ReAct-style agentic loop (Reason → Act → Observe) that orchestrates skills to complete a task |
| `src/skills/calculator.py` | Safely evaluate math expressions (`sqrt`, `sin`, `pi`, `**`, …) |
| `src/skills/code_executor.py` | Execute Python snippets in a subprocess with a configurable timeout |
| `src/skills/file_manager.py` | Read / write / list / delete files inside a sandboxed directory |
| `src/skills/memory.py` | Persist and retrieve key-value facts across agent turns (JSON-backed) |
| `src/skills/weather.py` | Fetch current weather via [wttr.in](https://wttr.in) (no API key needed) |
| `src/skills/web_search.py` | Query the DuckDuckGo Instant Answer API |

---

## Quick start

```bash
pip install -r requirements.txt

# Start the MCP server (stdio transport by default)
python -m src.mcp_server
```

### Using skills directly

```python
from src.skills import CalculatorSkill, WebSearchSkill

calc = CalculatorSkill()
print(calc.run("sqrt(144) + 2 ** 10"))   # → 1036.0

search = WebSearchSkill()
print(search.run("Model Context Protocol"))
```

### Running the agent

```python
from src.agent import Agent
from src.skills import CalculatorSkill, MemorySkill

agent = Agent(skills=[CalculatorSkill(), MemorySkill()])
result = agent.run("What is (17 ** 2) + (13 ** 2)?")
print(result)
```

The agent accepts any callable `llm` that maps a prompt string to a response
string, making it easy to plug in Anthropic, OpenAI, or any other model:

```python
import anthropic
from src.agent import Agent

client = anthropic.Anthropic()

def my_llm(prompt: str) -> str:
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

agent = Agent(llm=my_llm)
result = agent.run("Search the web for the latest MCP news and summarise it.")
print(result)
```

---

## Running tests

```bash
pytest
```

All 57 tests should pass.

---

## Architecture

```
MCP Client (Claude Desktop / any MCP host)
        │
        │ MCP protocol (stdio / SSE / HTTP)
        ▼
  src/mcp_server.py   ← FastMCP server
        │ calls
        ▼
  src/skills/*        ← individual skill modules
```

For autonomous task completion use `src/agent.py` which implements the
**ReAct** (Reason + Act) loop:

```
Task
 └─▶ [LLM reasons] ──▶ Thought
                    └─▶ Action: skill(args)
                              │
                    ┌─────────┘
                    ▼
               Observation
                    │
                    └─▶ [LLM reasons again] … until Final answer
```
