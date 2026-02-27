"""Agentic loop – ReAct-style (Reason + Act) agent that uses skills to complete tasks.

The agent works in discrete steps:

1. **Reason** – decide which skill (tool) to use and with what arguments.
2. **Act**    – call the skill and collect the observation.
3. **Observe** – incorporate the observation and decide whether the task is done.

This module is LLM-agnostic.  By default a simple ``EchoLLM`` mock is used so
that the agent can be tested without a real language model.  Swap it with any
callable that matches the ``LLMCallable`` protocol.

Usage example::

    from src.agent import Agent
    from src.skills import CalculatorSkill, WebSearchSkill

    agent = Agent(skills=[CalculatorSkill(), WebSearchSkill()])
    result = agent.run("What is 42 * 73?")
    print(result)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


# ---------------------------------------------------------------------------
# Type helpers
# ---------------------------------------------------------------------------

class LLMCallable(Protocol):
    """A callable that takes a prompt string and returns a response string."""

    def __call__(self, prompt: str) -> str:
        ...


# ---------------------------------------------------------------------------
# Step & trajectory
# ---------------------------------------------------------------------------

@dataclass
class Step:
    """One iteration of the ReAct loop."""

    thought: str
    tool: str
    tool_input: dict[str, Any]
    observation: str = ""

    def __str__(self) -> str:
        return (
            f"Thought: {self.thought}\n"
            f"Action: {self.tool}({json.dumps(self.tool_input)})\n"
            f"Observation: {self.observation}"
        )


@dataclass
class AgentResult:
    """Final result returned by ``Agent.run``."""

    answer: str
    steps: list[Step] = field(default_factory=list)
    success: bool = True

    def __str__(self) -> str:
        header = "\n".join(str(s) for s in self.steps)
        return f"{header}\nFinal answer: {self.answer}" if header else self.answer


# ---------------------------------------------------------------------------
# Default "mock" LLM – parses explicit JSON-based action commands
# ---------------------------------------------------------------------------

_ACTION_RE = re.compile(
    r'Action:\s*(\w+)\((\{.*?\})\)',
    re.DOTALL,
)
_FINAL_RE = re.compile(r'Final answer:\s*(.+)', re.DOTALL)


class EchoLLM:
    """
    Minimal mock LLM that understands a simple action syntax.

    It is intended for testing only.  Real usage should replace this with
    an actual language model (e.g. via the Anthropic or OpenAI SDK).

    The LLM prompt is expected to contain lines like::

        Action: calculator({"expression": "2 + 2"})

    or::

        Final answer: The result is 4.
    """

    def __call__(self, prompt: str) -> str:
        # Re-echo any Action or Final answer lines already present so that
        # unit tests can drive the agent deterministically.
        for line in reversed(prompt.splitlines()):
            if line.startswith("Action:") or line.startswith("Final answer:"):
                return line
        return "Final answer: (no action taken)"


# ---------------------------------------------------------------------------
# Skill dispatcher
# ---------------------------------------------------------------------------

class SkillDispatcher:
    """Route tool calls to the correct skill instance."""

    def __init__(self, skills: list[Any]) -> None:
        self._skills: dict[str, Any] = {s.name: s for s in skills}

    @property
    def tool_descriptions(self) -> str:
        lines = []
        for name, skill in self._skills.items():
            lines.append(f"- {name}: {skill.description}")
        return "\n".join(lines)

    def call(self, tool: str, tool_input: dict[str, Any]) -> str:
        skill = self._skills.get(tool)
        if skill is None:
            available = ", ".join(self._skills)
            return f"Error: unknown tool {tool!r}. Available: {available}"
        try:
            return skill.run(**tool_input)
        except TypeError as exc:
            return f"Error: bad arguments for {tool!r} – {exc}"
        except Exception as exc:
            return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a capable AI agent. Use the tools below to complete the task.

Available tools:
{tools}

Format each step as:
  Thought: <your reasoning>
  Action: <tool_name>({{"key": "value"}})

When you have the final answer:
  Final answer: <answer>

Task: {task}
"""


class Agent:
    """
    ReAct-style agentic loop.

    Parameters
    ----------
    skills:
        List of skill instances.  Each must have a ``name``, ``description``,
        and ``run(**kwargs)`` method.
    llm:
        A callable that accepts a prompt string and returns a response string.
        Defaults to :class:`EchoLLM` (testing mock).
    max_steps:
        Maximum number of Reason/Act iterations before giving up (default 10).
    """

    def __init__(
        self,
        skills: list[Any] | None = None,
        llm: LLMCallable | None = None,
        max_steps: int = 10,
    ) -> None:
        from src.skills import ALL_SKILLS

        skill_instances = [s() for s in ALL_SKILLS] if skills is None else skills
        self._dispatcher = SkillDispatcher(skill_instances)
        self._llm: LLMCallable = llm if llm is not None else EchoLLM()
        self._max_steps = max_steps

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, task: str) -> AgentResult:
        """
        Execute *task* using the agentic loop.

        Parameters
        ----------
        task:
            Natural language task description.

        Returns
        -------
        AgentResult
            Contains the final answer and the list of steps taken.
        """
        prompt = _SYSTEM_PROMPT.format(
            tools=self._dispatcher.tool_descriptions,
            task=task,
        )
        steps: list[Step] = []

        for _ in range(self._max_steps):
            response = self._llm(prompt)

            # Check for final answer first
            final_match = _FINAL_RE.search(response)
            if final_match:
                return AgentResult(
                    answer=final_match.group(1).strip(),
                    steps=steps,
                    success=True,
                )

            # Parse action
            action_match = _ACTION_RE.search(response)
            if action_match:
                tool = action_match.group(1)
                try:
                    tool_input = json.loads(action_match.group(2))
                except json.JSONDecodeError as exc:
                    observation = f"Error: could not parse tool input – {exc}"
                    tool_input = {}
                else:
                    observation = self._dispatcher.call(tool, tool_input)

                thought_match = re.search(r'Thought:\s*(.+?)(?:\n|$)', response)
                thought = thought_match.group(1).strip() if thought_match else ""

                step = Step(
                    thought=thought,
                    tool=tool,
                    tool_input=tool_input,
                    observation=observation,
                )
                steps.append(step)

                # Append observation to prompt so the LLM can continue
                prompt += f"\n{response}\nObservation: {observation}\n"
                continue

            # No parseable response – stop
            break

        return AgentResult(
            answer="Agent could not complete the task within the step limit.",
            steps=steps,
            success=False,
        )
