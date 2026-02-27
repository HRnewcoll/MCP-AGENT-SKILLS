"""Tests for individual AI skills."""

import os
import tempfile

import pytest

from src.skills.calculator import CalculatorSkill
from src.skills.code_executor import CodeExecutorSkill
from src.skills.file_manager import FileManagerSkill
from src.skills.memory import MemorySkill


# ---------------------------------------------------------------------------
# CalculatorSkill
# ---------------------------------------------------------------------------

class TestCalculatorSkill:
    skill = CalculatorSkill()

    def test_addition(self):
        assert self.skill.run("2 + 3") == "5"

    def test_multiplication(self):
        assert self.skill.run("6 * 7") == "42"

    def test_power(self):
        assert self.skill.run("2 ** 10") == "1024"

    def test_float_division(self):
        assert self.skill.run("1 / 4") == "0.25"

    def test_sqrt(self):
        assert self.skill.run("sqrt(144)") == "12.0"

    def test_pi(self):
        import math
        result = float(self.skill.run("pi"))
        assert abs(result - math.pi) < 1e-9

    def test_nested_expression(self):
        assert self.skill.run("(2 + 3) * (4 - 1)") == "15"

    def test_division_by_zero(self):
        result = self.skill.run("1 / 0")
        assert result.startswith("Error:")

    def test_invalid_expression(self):
        result = self.skill.run("import os")
        assert result.startswith("Error:")

    def test_unknown_name(self):
        result = self.skill.run("evil_func()")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# CodeExecutorSkill
# ---------------------------------------------------------------------------

class TestCodeExecutorSkill:
    skill = CodeExecutorSkill()

    def test_hello_world(self):
        result = self.skill.run('print("hello")')
        assert "hello" in result

    def test_arithmetic(self):
        result = self.skill.run("print(2 + 2)")
        assert "4" in result

    def test_multiline(self):
        code = "x = 10\ny = 20\nprint(x + y)"
        result = self.skill.run(code)
        assert "30" in result

    def test_stderr_captured(self):
        result = self.skill.run("import sys; sys.stderr.write('err')")
        assert "err" in result

    def test_timeout(self):
        result = self.skill.run("import time; time.sleep(60)", timeout=1)
        assert "Error" in result

    def test_syntax_error(self):
        result = self.skill.run("def f(:")
        assert "Error" in result or "SyntaxError" in result


# ---------------------------------------------------------------------------
# FileManagerSkill
# ---------------------------------------------------------------------------

class TestFileManagerSkill:
    def _make_skill(self):
        tmpdir = tempfile.mkdtemp()
        return FileManagerSkill(root=tmpdir)

    def test_write_and_read(self):
        skill = self._make_skill()
        assert skill.run("write", "hello.txt", "world") == "Written 5 bytes to 'hello.txt'"
        assert skill.run("read", "hello.txt") == "world"

    def test_list_empty(self):
        skill = self._make_skill()
        assert skill.run("list") == "(empty)"

    def test_list_after_write(self):
        skill = self._make_skill()
        skill.run("write", "a.txt", "a")
        skill.run("write", "b.txt", "b")
        listing = skill.run("list")
        assert "a.txt" in listing
        assert "b.txt" in listing

    def test_delete(self):
        skill = self._make_skill()
        skill.run("write", "del.txt", "bye")
        result = skill.run("delete", "del.txt")
        assert "Deleted" in result
        assert skill.run("read", "del.txt").startswith("Error:")

    def test_read_missing(self):
        skill = self._make_skill()
        assert skill.run("read", "ghost.txt").startswith("Error:")

    def test_path_traversal_blocked(self):
        skill = self._make_skill()
        result = skill.run("read", "../../etc/passwd")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        skill = self._make_skill()
        assert skill.run("explode").startswith("Error:")


# ---------------------------------------------------------------------------
# MemorySkill
# ---------------------------------------------------------------------------

class TestMemorySkill:
    def _make_skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        return MemorySkill(store_path=f.name)

    def test_set_and_get(self):
        skill = self._make_skill()
        assert skill.run("set", key="name", value="Alice") == "Stored 'name'"
        assert skill.run("get", key="name") == "Alice"

    def test_get_missing(self):
        skill = self._make_skill()
        assert skill.run("get", key="unknown").startswith("Error:")

    def test_delete(self):
        skill = self._make_skill()
        skill.run("set", key="x", value="1")
        assert "Deleted" in skill.run("delete", key="x")
        assert skill.run("get", key="x").startswith("Error:")

    def test_list(self):
        skill = self._make_skill()
        skill.run("set", key="a", value="1")
        skill.run("set", key="b", value="2")
        listing = skill.run("list")
        assert "a" in listing
        assert "b" in listing

    def test_clear(self):
        skill = self._make_skill()
        skill.run("set", key="k", value="v")
        result = skill.run("clear")
        assert "Cleared" in result
        assert skill.run("list") == "(no memories stored)"

    def test_persistence(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        s1 = MemorySkill(store_path=f.name)
        s1.run("set", key="persistent", value="yes")
        s2 = MemorySkill(store_path=f.name)
        assert s2.run("get", key="persistent") == "yes"

    def test_unknown_action(self):
        skill = self._make_skill()
        assert skill.run("explode").startswith("Error:")
