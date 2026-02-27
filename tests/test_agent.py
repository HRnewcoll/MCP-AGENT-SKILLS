"""Tests for the agentic loop (Agent, EchoLLM, SkillDispatcher)."""

import pytest

from src.agent import Agent, AgentResult, EchoLLM, SkillDispatcher, Step
from src.skills.calculator import CalculatorSkill
from src.skills.memory import MemorySkill


# ---------------------------------------------------------------------------
# EchoLLM
# ---------------------------------------------------------------------------

class TestEchoLLM:
    llm = EchoLLM()

    def test_echoes_action_line(self):
        prompt = 'Action: calculator({"expression": "1+1"})'
        assert self.llm(prompt) == prompt

    def test_echoes_final_answer(self):
        prompt = "Final answer: 42"
        assert self.llm(prompt) == prompt

    def test_fallback_when_nothing_found(self):
        result = self.llm("some random prompt")
        assert "Final answer" in result


# ---------------------------------------------------------------------------
# SkillDispatcher
# ---------------------------------------------------------------------------

class TestSkillDispatcher:
    def _dispatcher(self):
        return SkillDispatcher([CalculatorSkill()])

    def test_known_tool(self):
        d = self._dispatcher()
        result = d.call("calculator", {"expression": "2+2"})
        assert result == "4"

    def test_unknown_tool(self):
        d = self._dispatcher()
        result = d.call("blaster", {})
        assert result.startswith("Error:")
        assert "blaster" in result

    def test_bad_arguments(self):
        d = self._dispatcher()
        result = d.call("calculator", {"wrong_arg": "x"})
        assert "Error" in result

    def test_tool_descriptions_listed(self):
        d = self._dispatcher()
        assert "calculator" in d.tool_descriptions


# ---------------------------------------------------------------------------
# Agent (driven by a deterministic scripted LLM)
# ---------------------------------------------------------------------------

class ScriptedLLM:
    """Replays a fixed sequence of responses regardless of the prompt."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = iter(responses)

    def __call__(self, prompt: str) -> str:
        return next(self._responses)


class TestAgent:
    def test_single_tool_call(self):
        llm = ScriptedLLM([
            'Thought: need to add\nAction: calculator({"expression": "7 + 8"})',
            "Final answer: 15",
        ])
        agent = Agent(skills=[CalculatorSkill()], llm=llm)
        result = agent.run("What is 7 + 8?")
        assert result.success
        assert result.answer == "15"
        assert len(result.steps) == 1
        assert result.steps[0].observation == "15"

    def test_final_answer_immediately(self):
        llm = ScriptedLLM(["Final answer: I already know this is 42."])
        agent = Agent(skills=[CalculatorSkill()], llm=llm)
        result = agent.run("What is the answer to life?")
        assert result.success
        assert "42" in result.answer
        assert result.steps == []

    def test_max_steps_exceeded(self):
        # LLM never emits a Final answer
        llm = ScriptedLLM(
            ['Action: calculator({"expression": "1+1"})'] * 20
        )
        agent = Agent(skills=[CalculatorSkill()], llm=llm, max_steps=3)
        result = agent.run("loop forever")
        assert not result.success
        assert len(result.steps) == 3

    def test_invalid_json_in_action(self):
        llm = ScriptedLLM([
            "Action: calculator({bad json})",
            "Final answer: gave up",
        ])
        agent = Agent(skills=[CalculatorSkill()], llm=llm)
        result = agent.run("task")
        assert result.steps[0].observation.startswith("Error:")

    def test_multiple_steps(self):
        import tempfile

        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        mem = MemorySkill(store_path=f.name)
        llm = ScriptedLLM([
            'Thought: store name\nAction: memory({"action": "set", "key": "greeting", "value": "hello"})',
            'Thought: retrieve name\nAction: memory({"action": "get", "key": "greeting"})',
            "Final answer: hello",
        ])
        agent = Agent(skills=[mem], llm=llm)
        result = agent.run("store and retrieve greeting")
        assert result.success
        assert result.answer == "hello"
        assert len(result.steps) == 2

    def test_agent_str_representation(self):
        llm = ScriptedLLM(["Final answer: done"])
        agent = Agent(skills=[CalculatorSkill()], llm=llm)
        result = agent.run("anything")
        # AgentResult __str__ should not raise
        text = str(result)
        assert isinstance(text, str)

    def test_default_skills_loaded(self):
        """Agent instantiated without explicit skills loads all default skills."""
        from src.skills import ALL_SKILLS

        llm = ScriptedLLM(["Final answer: ok"])
        agent = Agent(llm=llm)
        result = agent.run("ping")
        assert result.success
        # All default skills should be registered
        for skill_cls in ALL_SKILLS:
            assert skill_cls.name in agent._dispatcher._skills
