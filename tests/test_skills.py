"""Tests for individual AI skills."""

import os
import tempfile

import pytest

from src.skills.agent_swarm import AgentSwarmSkill
from src.skills.calculator import CalculatorSkill
from src.skills.code_executor import CodeExecutorSkill
from src.skills.disclawd import DisclawdSkill
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


# ---------------------------------------------------------------------------
# DatetimeSkill
# ---------------------------------------------------------------------------

class TestDatetimeSkill:
    from src.skills.datetime_skill import DatetimeSkill
    skill = DatetimeSkill()

    def test_now_returns_utc(self):
        result = self.skill.run("now")
        assert "UTC" in result

    def test_parse_iso(self):
        assert self.skill.run("parse", date="2024-06-15") == "2024-06-15T00:00:00"

    def test_format(self):
        assert self.skill.run("format", date="2024-06-15", fmt="%d/%m/%Y") == "15/06/2024"

    def test_diff(self):
        result = self.skill.run("diff", date="2024-01-01", date2="2024-01-08")
        assert "7 days" in result

    def test_add_days(self):
        assert self.skill.run("add", date="2024-01-01", days=10, fmt="%Y-%m-%d") == "2024-01-11"

    def test_unknown_action(self):
        assert self.skill.run("explode").startswith("Error:")

    def test_invalid_date(self):
        assert self.skill.run("parse", date="not-a-date").startswith("Error:")


# ---------------------------------------------------------------------------
# TextProcessorSkill
# ---------------------------------------------------------------------------

class TestTextProcessorSkill:
    from src.skills.text_processor import TextProcessorSkill
    skill = TextProcessorSkill()

    def test_uppercase(self):
        assert self.skill.run("uppercase", text="hello") == "HELLO"

    def test_lowercase(self):
        assert self.skill.run("lowercase", text="WORLD") == "world"

    def test_word_count(self):
        assert self.skill.run("word_count", text="one two three") == "3"

    def test_char_count(self):
        assert self.skill.run("char_count", text="abc") == "3"

    def test_reverse(self):
        assert self.skill.run("reverse", text="abc") == "cba"

    def test_truncate(self):
        assert self.skill.run("truncate", text="hello world", max_length=5) == "hello..."

    def test_replace(self):
        assert self.skill.run("replace", text="foo bar", find="foo", replace_with="baz") == "baz bar"

    def test_snake_case(self):
        assert self.skill.run("snake_case", text="Hello World") == "hello_world"

    def test_camel_case(self):
        assert self.skill.run("camel_case", text="hello world") == "helloWorld"

    def test_unknown_action(self):
        assert self.skill.run("explode").startswith("Error:")


# ---------------------------------------------------------------------------
# DataConverterSkill
# ---------------------------------------------------------------------------

class TestDataConverterSkill:
    from src.skills.data_converter import DataConverterSkill
    skill = DataConverterSkill()

    def test_json_format(self):
        result = self.skill.run("json_format", data='{"b":2,"a":1}', indent=2)
        assert '"a"' in result and '"b"' in result

    def test_json_minify(self):
        result = self.skill.run("json_minify", data='{"a": 1, "b": 2}')
        assert " " not in result

    def test_base64_roundtrip(self):
        encoded = self.skill.run("base64_encode", data="hello")
        assert self.skill.run("base64_decode", data=encoded) == "hello"

    def test_hex_roundtrip(self):
        encoded = self.skill.run("hex_encode", data="hi")
        assert self.skill.run("hex_decode", data=encoded) == "hi"

    def test_url_encode(self):
        assert self.skill.run("url_encode", data="hello world") == "hello%20world"

    def test_url_decode(self):
        assert self.skill.run("url_decode", data="hello%20world") == "hello world"

    def test_csv_to_json(self):
        assert "Alice" in self.skill.run("csv_to_json", data="name,age\nAlice,30")

    def test_json_to_csv(self):
        assert "Alice" in self.skill.run("json_to_csv", data='[{"name":"Alice","age":30}]')

    def test_unknown_action(self):
        assert self.skill.run("explode").startswith("Error:")


# ---------------------------------------------------------------------------
# SystemInfoSkill
# ---------------------------------------------------------------------------

class TestSystemInfoSkill:
    from src.skills.system_info import SystemInfoSkill
    skill = SystemInfoSkill()

    def test_os_info(self):
        assert "System" in self.skill.run("os")

    def test_python_info(self):
        assert "Version" in self.skill.run("python")

    def test_cwd(self):
        import os as _os
        assert self.skill.run("cwd") == _os.getcwd()

    def test_all(self):
        result = self.skill.run("all")
        assert "OS" in result and "Python" in result

    def test_unknown_action(self):
        assert self.skill.run("explode").startswith("Error:")


# ---------------------------------------------------------------------------
# TaskListSkill
# ---------------------------------------------------------------------------

class TestTaskListSkill:
    def _make_skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        from src.skills.task_list import TaskListSkill
        return TaskListSkill(store_path=f.name)

    def test_add_and_list(self):
        skill = self._make_skill()
        skill.run("add", title="Buy milk")
        assert "Buy milk" in skill.run("list")

    def test_complete(self):
        skill = self._make_skill()
        skill.run("add", title="Task A")
        assert "completed" in skill.run("complete", task_id=1)
        assert "[x]" in skill.run("list")

    def test_uncomplete(self):
        skill = self._make_skill()
        skill.run("add", title="Task B")
        skill.run("complete", task_id=1)
        skill.run("uncomplete", task_id=1)
        assert "[ ]" in skill.run("list")

    def test_delete(self):
        skill = self._make_skill()
        skill.run("add", title="Delete me")
        skill.run("delete", task_id=1)
        assert "(no tasks)" in skill.run("list")

    def test_clear(self):
        skill = self._make_skill()
        skill.run("add", title="A")
        assert "Cleared" in skill.run("clear")

    def test_unknown_action(self):
        assert self._make_skill().run("explode").startswith("Error:")


# ---------------------------------------------------------------------------
# DiffToolSkill
# ---------------------------------------------------------------------------

class TestDiffToolSkill:
    from src.skills.diff_tool import DiffToolSkill
    skill = DiffToolSkill()

    def test_unified_no_diff(self):
        assert self.skill.run("unified", text_a="abc", text_b="abc") == "(no differences)"

    def test_unified_with_diff(self):
        result = self.skill.run("unified", text_a="hello\n", text_b="world\n")
        assert "-hello" in result or "+world" in result

    def test_ratio_identical(self):
        assert "1.0000" in self.skill.run("ratio", text_a="abc", text_b="abc")

    def test_ratio_different(self):
        assert "Similarity" in self.skill.run("ratio", text_a="abc", text_b="xyz")

    def test_unknown_action(self):
        assert self.skill.run("explode").startswith("Error:")


# ---------------------------------------------------------------------------
# RegexToolSkill
# ---------------------------------------------------------------------------

class TestRegexToolSkill:
    from src.skills.regex_tool import RegexToolSkill
    skill = RegexToolSkill()

    def test_match(self):
        assert "123" in self.skill.run("match", pattern=r"\d+", text="123abc")

    def test_no_match(self):
        assert self.skill.run("match", pattern=r"\d+", text="abc") == "No match"

    def test_findall(self):
        assert "3 match" in self.skill.run("findall", pattern=r"\d+", text="a1b2c3")

    def test_replace(self):
        assert self.skill.run("replace", pattern=r"\d+", text="a1b2", replacement="X") == "aXbX"

    def test_validate_pass(self):
        assert "Valid" in self.skill.run("validate", pattern=r"\d{3}", text="123")

    def test_validate_fail(self):
        assert "Invalid" in self.skill.run("validate", pattern=r"\d{3}", text="12")

    def test_invalid_pattern(self):
        assert self.skill.run("match", pattern="[unclosed", text="x").startswith("Error:")

    def test_case_insensitive_flag(self):
        assert "HELLO" in self.skill.run("match", pattern="hello", text="HELLO", flags="i")


# ---------------------------------------------------------------------------
# HashToolSkill
# ---------------------------------------------------------------------------

class TestHashToolSkill:
    from src.skills.hash_tool import HashToolSkill
    skill = HashToolSkill()

    def test_empty_text_rejected(self):
        assert self.skill.run("sha256", text="").startswith("Error:")

    def test_sha256_known(self):
        result = self.skill.run("sha256", text="hello")
        assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_md5_known(self):
        assert self.skill.run("md5", text="hello") == "5d41402abc4b2a76b9719d911017c592"

    def test_blake2b_length(self):
        assert len(self.skill.run("blake2b", text="hello")) == 128

    def test_hmac_requires_secret(self):
        assert self.skill.run("hmac_sha256", text="msg").startswith("Error:")

    def test_hmac_sha256(self):
        assert len(self.skill.run("hmac_sha256", text="msg", secret="key")) == 64

    def test_unknown_action(self):
        assert self.skill.run("explode", text="x").startswith("Error:")


# ---------------------------------------------------------------------------
# UnitConverterSkill
# ---------------------------------------------------------------------------

class TestUnitConverterSkill:
    from src.skills.unit_converter import UnitConverterSkill
    skill = UnitConverterSkill()

    def test_km_to_m(self):
        assert "1000" in self.skill.run("length", 1.0, "km", "m")

    def test_celsius_to_fahrenheit(self):
        assert "32" in self.skill.run("temperature", 0.0, "c", "f")

    def test_kg_to_lb(self):
        assert "2.20" in self.skill.run("weight", 1.0, "kg", "lb")

    def test_unknown_category(self):
        assert self.skill.run("bananas", 1.0, "x", "y").startswith("Error:")

    def test_unknown_unit(self):
        assert self.skill.run("length", 1.0, "parsec", "m").startswith("Error:")


# ---------------------------------------------------------------------------
# RandomGeneratorSkill
# ---------------------------------------------------------------------------

class TestRandomGeneratorSkill:
    from src.skills.random_generator import RandomGeneratorSkill
    skill = RandomGeneratorSkill()

    def test_uuid(self):
        import re
        assert re.match(r"[0-9a-f\-]{36}", self.skill.run("uuid"))

    def test_hex_length(self):
        assert len(self.skill.run("hex", length=16)) == 16

    def test_password_length(self):
        assert len(self.skill.run("password", length=20)) == 20

    def test_integer_fixed(self):
        assert self.skill.run("integer", min_val=5, max_val=5) == "5"

    def test_choice(self):
        assert self.skill.run("choice", items="apple\nbanana\ncherry") in ("apple", "banana", "cherry")

    def test_shuffle(self):
        result = self.skill.run("shuffle", items="a\nb\nc\nd")
        assert sorted(result.splitlines()) == ["a", "b", "c", "d"]

    def test_unknown_action(self):
        assert self.skill.run("explode").startswith("Error:")


# ---------------------------------------------------------------------------
# ShellSkill
# ---------------------------------------------------------------------------

class TestShellSkill:
    from src.skills.shell_skill import ShellSkill
    skill = ShellSkill()

    def test_echo(self):
        assert "hello" in self.skill.run("echo hello")

    def test_timeout(self):
        assert "Error" in self.skill.run("sleep 60", timeout=1)

    def test_blocked_pattern(self):
        assert self.skill.run("rm -rf /").startswith("Error:")

    def test_empty_command(self):
        assert self.skill.run("").startswith("Error:")

    def test_stderr_captured(self):
        assert "err" in self.skill.run("echo err >&2")


# ---------------------------------------------------------------------------
# JsonProcessorSkill
# ---------------------------------------------------------------------------

class TestJsonProcessorSkill:
    from src.skills.json_processor import JsonProcessorSkill
    skill = JsonProcessorSkill()

    def test_parse(self):
        assert '"a"' in self.skill.run("parse", data='{"a":1}')

    def test_get_top_level(self):
        assert self.skill.run("get", data='{"a":1}', path="a") == "1"

    def test_get_nested(self):
        assert self.skill.run("get", data='{"a":{"b":42}}', path="a.b") == "42"

    def test_set(self):
        assert "updated" in self.skill.run("set", data='{"a":1}', path="a", value='"updated"')

    def test_delete(self):
        result = self.skill.run("delete", data='{"a":1,"b":2}', path="a")
        assert '"a"' not in result and '"b"' in result

    def test_keys(self):
        result = self.skill.run("keys", data='{"z":1,"a":2}')
        assert "a" in result and "z" in result

    def test_type_integer(self):
        assert self.skill.run("type", data='{"x":42}', path="x") == "integer"

    def test_flatten(self):
        assert "a.b: 1" in self.skill.run("flatten", data='{"a":{"b":1}}')

    def test_invalid_json(self):
        assert self.skill.run("parse", data="{bad}").startswith("Error:")

    def test_unknown_action(self):
        assert self.skill.run("explode", data="{}").startswith("Error:")


# ---------------------------------------------------------------------------
# NoteTakerSkill
# ---------------------------------------------------------------------------

class TestNoteTakerSkill:
    def _make_skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        from src.skills.note_taker import NoteTakerSkill
        return NoteTakerSkill(store_path=f.name)

    def test_add_and_list(self):
        skill = self._make_skill()
        skill.run("add", title="My Note", content="body text", tags="python,ai")
        assert "My Note" in skill.run("list")

    def test_get(self):
        skill = self._make_skill()
        skill.run("add", title="Get Me", content="some content")
        result = skill.run("get", note_id=1)
        assert "Get Me" in result and "some content" in result

    def test_update(self):
        skill = self._make_skill()
        skill.run("add", title="Old Title", content="old")
        skill.run("update", note_id=1, title="New Title")
        assert "New Title" in skill.run("get", note_id=1)

    def test_delete(self):
        skill = self._make_skill()
        skill.run("add", title="Del", content="x")
        skill.run("delete", note_id=1)
        assert "(no notes)" in skill.run("list")

    def test_search_by_keyword(self):
        skill = self._make_skill()
        skill.run("add", title="Python tips", content="useful")
        skill.run("add", title="Rust tips", content="other")
        result = skill.run("search", query="Python")
        assert "Python tips" in result and "Rust tips" not in result

    def test_search_by_tag(self):
        skill = self._make_skill()
        skill.run("add", title="Tagged", content="x", tags="ai,ml")
        assert "Tagged" in skill.run("search", query="#ai")

    def test_clear(self):
        skill = self._make_skill()
        skill.run("add", title="A", content="x")
        assert "Cleared" in skill.run("clear")

    def test_unknown_action(self):
        assert self._make_skill().run("explode").startswith("Error:")


# ---------------------------------------------------------------------------
# HttpRequestSkill  (validation / SSRF tests only – no live network calls)
# ---------------------------------------------------------------------------

class TestHttpRequestSkill:
    from src.skills.http_request import HttpRequestSkill
    skill = HttpRequestSkill()

    def test_missing_url(self):
        assert self.skill.run("get", url="").startswith("Error:")

    def test_invalid_scheme(self):
        assert self.skill.run("get", url="ftp://example.com").startswith("Error:")

    def test_loopback_blocked(self):
        assert self.skill.run("get", url="http://127.0.0.1/").startswith("Error:")

    def test_localhost_blocked(self):
        assert self.skill.run("get", url="http://localhost/").startswith("Error:")

    def test_invalid_headers_json(self):
        assert self.skill.run("get", url="https://example.com", headers="{bad}").startswith("Error:")

    def test_unknown_action(self):
        assert self.skill.run("explode", url="https://example.com").startswith("Error:")


# ---------------------------------------------------------------------------
# AgentSwarmSkill
# ---------------------------------------------------------------------------

class TestAgentSwarmSkill:
    """Tests for the AgentSwarm (Company) skill."""

    def _skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        return AgentSwarmSkill(store_path=f.name)

    def test_create_company_website(self):
        skill = self._skill()
        result = skill.run("create_company", goal="build a website")
        assert "Company created" in result
        assert "website" in result.lower()
        assert "CEO" in result or "Developer" in result

    def test_create_company_default(self):
        skill = self._skill()
        result = skill.run("create_company", goal="do something cool")
        assert "Company created" in result

    def test_create_company_missing_goal(self):
        skill = self._skill()
        result = skill.run("create_company")
        assert result.startswith("Error:")

    def test_list_agents_empty(self):
        skill = self._skill()
        result = skill.run("list_agents")
        assert "no agents" in result

    def test_list_agents_after_create(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        result = skill.run("list_agents")
        assert "CEO" in result or "Developer" in result

    def test_get_agent(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        result = skill.run("get_agent", agent_id=1)
        assert "Agent #1" in result
        assert "Role" in result

    def test_get_agent_not_found(self):
        skill = self._skill()
        result = skill.run("get_agent", agent_id=999)
        assert result.startswith("Error:")

    def test_add_agents(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        result = skill.run("add_agents", role="Marketing Manager", count=2, level="senior")
        assert "Marketing Manager" in result
        assert "2" in result

    def test_add_agents_missing_role(self):
        skill = self._skill()
        result = skill.run("add_agents", count=1)
        assert result.startswith("Error:")

    def test_assign_task(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        result = skill.run("assign_task", agent_id=1, task="Design the homepage")
        assert "Design the homepage" in result

    def test_assign_task_missing_agent_id(self):
        skill = self._skill()
        result = skill.run("assign_task", task="Do something")
        assert result.startswith("Error:")

    def test_assign_task_missing_task(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        result = skill.run("assign_task", agent_id=1)
        assert result.startswith("Error:")

    def test_complete_task(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        skill.run("assign_task", agent_id=1, task="Set project direction")
        result = skill.run("complete_task", agent_id=1)
        assert "completed" in result.lower()

    def test_complete_task_no_active_task(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        result = skill.run("complete_task", agent_id=1)
        assert result.startswith("Error:")

    def test_status(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        result = skill.run("status")
        assert "Goal" in result
        assert "Total agents" in result

    def test_clear(self):
        skill = self._skill()
        skill.run("create_company", goal="build a website")
        result = skill.run("clear")
        assert "cleared" in result.lower()
        assert skill.run("list_agents") == "(no agents – use create_company first)"

    def test_unknown_action(self):
        skill = self._skill()
        result = skill.run("explode")
        assert result.startswith("Error:")

    def test_persistence(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        skill1 = AgentSwarmSkill(store_path=f.name)
        skill1.run("create_company", goal="build a website")

        skill2 = AgentSwarmSkill(store_path=f.name)
        result = skill2.run("list_agents")
        assert "CEO" in result or "Developer" in result

    def test_marketing_company(self):
        skill = self._skill()
        result = skill.run("create_company", goal="create a marketing campaign")
        assert "Company created" in result
        assert "Marketing" in result or "CMO" in result

    def test_security_company(self):
        skill = self._skill()
        result = skill.run("create_company", goal="security audit")
        assert "Company created" in result
        assert "Penetration Tester" in result or "CISO" in result


# ---------------------------------------------------------------------------
# DisclawdSkill
# ---------------------------------------------------------------------------

class TestDisclawdSkill:
    """Tests for the Disclawd Discord-like messaging skill."""

    def _skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        return DisclawdSkill(store_path=f.name)

    def test_create_server(self):
        skill = self._skill()
        result = skill.run("create_server", name="MyProject")
        assert "MyProject" in result
        assert result.startswith("Created server")

    def test_create_server_missing_name(self):
        skill = self._skill()
        result = skill.run("create_server")
        assert result.startswith("Error:")

    def test_create_server_duplicate(self):
        skill = self._skill()
        skill.run("create_server", name="Alpha")
        result = skill.run("create_server", name="Alpha")
        assert result.startswith("Error:")

    def test_list_servers_empty(self):
        skill = self._skill()
        assert skill.run("list_servers") == "(no servers)"

    def test_list_servers(self):
        skill = self._skill()
        skill.run("create_server", name="Project1")
        result = skill.run("list_servers")
        assert "Project1" in result

    def test_create_channel(self):
        skill = self._skill()
        skill.run("create_server", name="Hub")
        result = skill.run("create_channel", server="Hub", channel="general")
        assert "#general" in result
        assert "Hub" in result

    def test_create_channel_missing_server(self):
        skill = self._skill()
        result = skill.run("create_channel", channel="general")
        assert result.startswith("Error:")

    def test_create_channel_missing_name(self):
        skill = self._skill()
        skill.run("create_server", name="Hub")
        result = skill.run("create_channel", server="Hub")
        assert result.startswith("Error:")

    def test_create_channel_duplicate(self):
        skill = self._skill()
        skill.run("create_server", name="Hub")
        skill.run("create_channel", server="Hub", channel="dev")
        result = skill.run("create_channel", server="Hub", channel="dev")
        assert result.startswith("Error:")

    def test_create_channel_unknown_server(self):
        skill = self._skill()
        result = skill.run("create_channel", server="Ghost", channel="dev")
        assert result.startswith("Error:")

    def test_list_channels(self):
        skill = self._skill()
        skill.run("create_server", name="Hub")
        skill.run("create_channel", server="Hub", channel="general")
        skill.run("create_channel", server="Hub", channel="dev")
        result = skill.run("list_channels", server="Hub")
        assert "#general" in result
        assert "#dev" in result

    def test_list_channels_empty(self):
        skill = self._skill()
        skill.run("create_server", name="Empty")
        result = skill.run("list_channels", server="Empty")
        assert "no channels" in result

    def test_post_message(self):
        skill = self._skill()
        skill.run("create_server", name="Office")
        skill.run("create_channel", server="Office", channel="general")
        result = skill.run(
            "post_message",
            server="Office",
            channel="general",
            author="CEO",
            message="Welcome everyone!",
        )
        assert "CEO" in result
        assert "Welcome everyone!" in result

    def test_post_message_missing_author(self):
        skill = self._skill()
        skill.run("create_server", name="Office")
        skill.run("create_channel", server="Office", channel="general")
        result = skill.run("post_message", server="Office", channel="general", message="Hi")
        assert result.startswith("Error:")

    def test_post_message_missing_content(self):
        skill = self._skill()
        skill.run("create_server", name="Office")
        skill.run("create_channel", server="Office", channel="general")
        result = skill.run("post_message", server="Office", channel="general", author="Alex")
        assert result.startswith("Error:")

    def test_post_message_unknown_channel(self):
        skill = self._skill()
        skill.run("create_server", name="Office")
        result = skill.run(
            "post_message",
            server="Office",
            channel="ghost",
            author="Sam",
            message="Hello",
        )
        assert result.startswith("Error:")

    def test_read_channel(self):
        skill = self._skill()
        skill.run("create_server", name="Office")
        skill.run("create_channel", server="Office", channel="general")
        skill.run("post_message", server="Office", channel="general", author="CEO", message="Msg1")
        skill.run("post_message", server="Office", channel="general", author="Dev", message="Msg2")
        result = skill.run("read_channel", server="Office", channel="general")
        assert "CEO" in result
        assert "Msg1" in result
        assert "Msg2" in result

    def test_read_channel_empty(self):
        skill = self._skill()
        skill.run("create_server", name="Office")
        skill.run("create_channel", server="Office", channel="silent")
        result = skill.run("read_channel", server="Office", channel="silent")
        assert "no messages" in result

    def test_read_channel_limit(self):
        skill = self._skill()
        skill.run("create_server", name="Office")
        skill.run("create_channel", server="Office", channel="log")
        for i in range(10):
            skill.run("post_message", server="Office", channel="log", author="Bot", message=f"msg{i}")
        result = skill.run("read_channel", server="Office", channel="log", limit=3)
        assert "msg9" in result
        assert "msg7" in result
        # msg0 should not appear (outside the last 3)
        assert "msg0" not in result

    def test_list_messages_alias(self):
        skill = self._skill()
        skill.run("create_server", name="Office")
        skill.run("create_channel", server="Office", channel="general")
        skill.run("post_message", server="Office", channel="general", author="A", message="hello")
        result = skill.run("list_messages", server="Office", channel="general")
        assert "hello" in result

    def test_delete_server(self):
        skill = self._skill()
        skill.run("create_server", name="ToDelete")
        result = skill.run("delete_server", server="ToDelete")
        assert "Deleted" in result
        assert skill.run("list_servers") == "(no servers)"

    def test_delete_server_unknown(self):
        skill = self._skill()
        result = skill.run("delete_server", server="Ghost")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        skill = self._skill()
        result = skill.run("broadcast")
        assert result.startswith("Error:")

    def test_persistence(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        skill1 = DisclawdSkill(store_path=f.name)
        skill1.run("create_server", name="Persistent")
        skill1.run("create_channel", server="Persistent", channel="general")
        skill1.run("post_message", server="Persistent", channel="general", author="Alex", message="Hi!")

        skill2 = DisclawdSkill(store_path=f.name)
        result = skill2.run("read_channel", server="Persistent", channel="general")
        assert "Hi!" in result


# ---------------------------------------------------------------------------
# Base64Skill
# ---------------------------------------------------------------------------

class TestBase64Skill:
    from src.skills.base64_skill import Base64Skill
    skill = Base64Skill()

    def test_encode_decode_b64(self):
        encoded = self.skill.run("encode_b64", data="hello world")
        assert encoded == "aGVsbG8gd29ybGQ="
        assert self.skill.run("decode_b64", data=encoded) == "hello world"

    def test_encode_decode_url(self):
        encoded = self.skill.run("encode_url", data="hello world")
        assert "%20" in encoded or "+" in encoded or encoded == "hello%20world"
        decoded = self.skill.run("decode_url", data=encoded)
        assert decoded == "hello world"

    def test_encode_decode_hex(self):
        encoded = self.skill.run("encode_hex", data="hi")
        assert self.skill.run("decode_hex", data=encoded) == "hi"

    def test_encode_decode_b32(self):
        encoded = self.skill.run("encode_b32", data="hello")
        assert self.skill.run("decode_b32", data=encoded) == "hello"

    def test_encode_decode_b16(self):
        encoded = self.skill.run("encode_b16", data="abc")
        assert self.skill.run("decode_b16", data=encoded) == "abc"

    def test_missing_data(self):
        result = self.skill.run("encode_url")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("foobar", data="x")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# CsvProcessorSkill
# ---------------------------------------------------------------------------

class TestCsvProcessorSkill:
    from src.skills.csv_processor import CsvProcessorSkill

    def _skill(self):
        return self.CsvProcessorSkill()

    def test_from_csv_string(self):
        skill = self._skill()
        result = skill.run("from_csv_string", text="name,age\nAlice,30\nBob,25")
        import json
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]["name"] == "Alice"

    def test_list_columns(self):
        skill = self._skill()
        skill.run("from_csv_string", text="a,b,c\n1,2,3")
        result = skill.run("list_columns")
        assert "a" in result and "b" in result and "c" in result

    def test_add_row(self):
        skill = self._skill()
        skill.run("from_csv_string", text="name,age\nAlice,30")
        result = skill.run("add_row", values="Charlie,40")
        assert "Added row" in result

    def test_get_row(self):
        skill = self._skill()
        skill.run("from_csv_string", text="name,age\nAlice,30\nBob,25")
        result = skill.run("get_row", row_index=1)
        assert "Bob" in result

    def test_delete_row(self):
        skill = self._skill()
        skill.run("from_csv_string", text="x,y\n1,2\n3,4")
        result = skill.run("delete_row", row_index=0)
        assert "Deleted row 0" in result

    def test_sort(self):
        skill = self._skill()
        skill.run("from_csv_string", text="name,age\nBob,25\nAlice,30")
        result = skill.run("sort", column="name")
        assert "Sorted" in result

    def test_to_json(self):
        skill = self._skill()
        skill.run("from_csv_string", text="x,y\n1,2")
        result = skill.run("to_json")
        import json
        data = json.loads(result)
        assert data[0]["x"] == "1"

    def test_get_rows_filter(self):
        skill = self._skill()
        skill.run("from_csv_string", text="name,age\nAlice,30\nBob,25")
        result = skill.run("get_rows", column="name", value="Alice")
        assert "Alice" in result

    def test_unknown_action(self):
        skill = self._skill()
        result = skill.run("teleport")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# MarkdownSkill
# ---------------------------------------------------------------------------

class TestMarkdownSkill:
    from src.skills.markdown_skill import MarkdownSkill
    skill = MarkdownSkill()

    def test_to_html_heading(self):
        result = self.skill.run("to_html", text="# Hello")
        assert "<h1>" in result and "Hello" in result

    def test_to_html_bold(self):
        result = self.skill.run("to_html", text="**bold**")
        assert "<strong>" in result

    def test_to_html_list(self):
        result = self.skill.run("to_html", text="- item1\n- item2")
        assert "<li>" in result

    def test_to_plain(self):
        result = self.skill.run("to_plain", text="# Header\n**bold**")
        assert "<" not in result
        assert "Header" in result

    def test_extract_links(self):
        result = self.skill.run("extract_links", text="Visit [Home](https://my-site.example/page)")
        assert "Home" in result and "my-site.example" in result

    def test_extract_headers(self):
        result = self.skill.run("extract_headers", text="# H1\n## H2")
        assert "H1" in result and "H2" in result

    def test_missing_text(self):
        result = self.skill.run("to_html")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("render")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# ColorConverterSkill
# ---------------------------------------------------------------------------

class TestColorConverterSkill:
    from src.skills.color_converter import ColorConverterSkill
    skill = ColorConverterSkill()

    def test_hex_to_rgb(self):
        result = self.skill.run("hex_to_rgb", hex_color="#ff0000")
        assert "255" in result and "0" in result

    def test_rgb_to_hex(self):
        result = self.skill.run("rgb_to_hex", r=255, g=0, b=0)
        assert result.lower() == "#ff0000"

    def test_hex_to_hsl(self):
        result = self.skill.run("hex_to_hsl", hex_color="#ff0000")
        assert "hsl(" in result

    def test_hsl_to_hex(self):
        result = self.skill.run("hsl_to_hex", h=0, s=100, l=50)
        assert result.startswith("#")

    def test_lighten(self):
        result = self.skill.run("lighten", hex_color="#808080", amount=10)
        assert result.startswith("#")

    def test_darken(self):
        result = self.skill.run("darken", hex_color="#808080", amount=10)
        assert result.startswith("#")

    def test_complementary(self):
        result = self.skill.run("complementary", hex_color="#ff0000")
        assert result.startswith("#")

    def test_mix(self):
        result = self.skill.run("mix", hex1="#000000", hex2="#ffffff", ratio=50)
        assert result.startswith("#")

    def test_invalid_hex(self):
        result = self.skill.run("hex_to_rgb", hex_color="ZZZZZZ")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("invert")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# WorldTimeSkill
# ---------------------------------------------------------------------------

class TestWorldTimeSkill:
    from src.skills.world_time import WorldTimeSkill
    skill = WorldTimeSkill()

    def test_now_utc(self):
        result = self.skill.run("now", timezone="UTC")
        assert not result.startswith("Error:")
        assert "UTC" in result

    def test_now_specific_zone(self):
        result = self.skill.run("now", timezone="America/New_York")
        assert not result.startswith("Error:")

    def test_offset(self):
        result = self.skill.run("offset", timezone="UTC")
        assert "UTC" in result

    def test_list_zones(self):
        result = self.skill.run("list_zones", filter_str="Europe")
        assert "Europe" in result

    def test_convert(self):
        result = self.skill.run(
            "convert", dt="2025-01-01 12:00:00", from_tz="UTC", to_tz="America/New_York"
        )
        assert not result.startswith("Error:")

    def test_invalid_timezone(self):
        result = self.skill.run("now", timezone="Fake/Zone")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("sleep")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# PasswordGeneratorSkill
# ---------------------------------------------------------------------------

class TestPasswordGeneratorSkill:
    from src.skills.password_generator import PasswordGeneratorSkill
    skill = PasswordGeneratorSkill()

    def test_generate_length(self):
        result = self.skill.run("generate", length=20)
        assert len(result) == 20

    def test_generate_no_symbols(self):
        result = self.skill.run("generate", length=16, symbols=False)
        assert not any(c in result for c in "!@#$%^&*()")

    def test_generate_passphrase(self):
        result = self.skill.run("generate_passphrase", words=3, separator="-")
        parts = result.split("-")
        assert len(parts) == 3

    def test_check_strength_strong(self):
        result = self.skill.run("check_strength", password="MyStr0ng!Pass#42")
        assert "Strong" in result or "Excellent" in result or "Very strong" in result

    def test_check_strength_weak(self):
        result = self.skill.run("check_strength", password="abc")
        assert "weak" in result.lower()

    def test_missing_password(self):
        result = self.skill.run("check_strength")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("crack")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# UrlParserSkill
# ---------------------------------------------------------------------------

class TestUrlParserSkill:
    from src.skills.url_parser import UrlParserSkill
    skill = UrlParserSkill()

    def test_parse(self):
        result = self.skill.run("parse", url="https://example.com/path?a=1&b=2")
        # Verify the parse output contains the host and a query param key
        assert "netloc" in result or "a" in result

    def test_build(self):
        result = self.skill.run("build", scheme="https", host="example.com", path="/test")
        assert "https://example.com/test" in result

    def test_encode_decode(self):
        encoded = self.skill.run("encode", text="hello world")
        assert "%" in encoded
        decoded = self.skill.run("decode", text=encoded)
        assert decoded == "hello world"

    def test_add_param(self):
        result = self.skill.run("add_param", url="https://example.com", key="foo", value="bar")
        assert "foo=bar" in result

    def test_remove_param(self):
        result = self.skill.run("remove_param", url="https://example.com?foo=bar&baz=1", key="foo")
        assert "foo" not in result

    def test_get_param(self):
        result = self.skill.run("get_param", url="https://example.com?q=hello", key="q")
        assert result == "hello"

    def test_extract_domain(self):
        result = self.skill.run("extract_domain", url="https://www.myapp.example/search")
        # extract_domain returns the full hostname including subdomains
        assert result == "www.myapp.example"

    def test_normalize(self):
        result = self.skill.run("normalize", url="HTTPS://Example.COM/path/")
        assert result == "https://example.com/path"

    def test_missing_url(self):
        result = self.skill.run("parse")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("crawl")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# NetworkToolsSkill
# ---------------------------------------------------------------------------

class TestNetworkToolsSkill:
    from src.skills.network_tools import NetworkToolsSkill
    skill = NetworkToolsSkill()

    def test_my_hostname(self):
        result = self.skill.run("my_hostname")
        assert not result.startswith("Error:")
        assert "hostname" in result

    def test_dns_lookup_localhost(self):
        result = self.skill.run("dns_lookup", host="localhost")
        assert not result.startswith("Error:")

    def test_missing_host(self):
        result = self.skill.run("dns_lookup")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("trace")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# TemplateSkill
# ---------------------------------------------------------------------------

class TestTemplateSkill:
    from src.skills.template_skill import TemplateSkill
    skill = TemplateSkill()

    def test_render_dollar_style(self):
        result = self.skill.run("render", template="Hello $name!", variables="name=World")
        assert result == "Hello World!"

    def test_render_brace_style(self):
        result = self.skill.run("render", template="Hi {{user}}", variables="user=Alice")
        assert result == "Hi Alice"

    def test_list_vars(self):
        result = self.skill.run("list_vars", template="$a and {{b}}")
        assert "a" in result and "b" in result

    def test_preview(self):
        result = self.skill.run("preview", template="Hello $name")
        assert "[" in result  # placeholders highlighted

    def test_missing_variable(self):
        result = self.skill.run("render", template="$missing", variables="")
        assert result.startswith("Error:")

    def test_missing_template(self):
        result = self.skill.run("render")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("compile")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# BudgetTrackerSkill
# ---------------------------------------------------------------------------

class TestBudgetTrackerSkill:
    from src.skills.budget_tracker import BudgetTrackerSkill

    def _skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        return self.BudgetTrackerSkill(store_path=f.name)

    def test_add_income(self):
        skill = self._skill()
        result = skill.run("add_income", amount=1000, category="Salary")
        assert "+$1000.00" in result

    def test_add_expense(self):
        skill = self._skill()
        result = skill.run("add_expense", amount=50, category="Food")
        assert "-$50.00" in result

    def test_balance(self):
        skill = self._skill()
        skill.run("add_income", amount=1000)
        skill.run("add_expense", amount=200)
        result = skill.run("balance")
        assert "$800.00" in result

    def test_list(self):
        skill = self._skill()
        skill.run("add_income", amount=100, description="bonus")
        result = skill.run("list")
        assert "income" in result

    def test_summary(self):
        skill = self._skill()
        skill.run("add_income", amount=500, category="Job")
        result = skill.run("summary")
        assert "Job" in result

    def test_delete(self):
        skill = self._skill()
        skill.run("add_income", amount=100)
        result = skill.run("delete", transaction_id=1)
        assert "Deleted" in result

    def test_invalid_amount(self):
        skill = self._skill()
        result = skill.run("add_income", amount=0)
        assert result.startswith("Error:")

    def test_clear(self):
        skill = self._skill()
        skill.run("add_income", amount=100)
        result = skill.run("clear")
        assert "Cleared" in result

    def test_unknown_action(self):
        skill = self._skill()
        result = skill.run("invest")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# FlashcardSkill
# ---------------------------------------------------------------------------

class TestFlashcardSkill:
    from src.skills.flashcard_skill import FlashcardSkill

    def _skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        return self.FlashcardSkill(store_path=f.name)

    def test_create_deck(self):
        skill = self._skill()
        result = skill.run("create_deck", deck="Python")
        assert "Python" in result

    def test_add_and_list_cards(self):
        skill = self._skill()
        skill.run("create_deck", deck="Math")
        skill.run("add_card", deck="Math", front="2+2?", back="4")
        result = skill.run("list_cards", deck="Math")
        assert "2+2?" in result

    def test_get_card(self):
        skill = self._skill()
        skill.run("create_deck", deck="Facts")
        skill.run("add_card", deck="Facts", front="Capital of France?", back="Paris")
        result = skill.run("get_card", deck="Facts", card_id=1)
        assert "Paris" in result

    def test_quiz(self):
        skill = self._skill()
        skill.run("create_deck", deck="Q")
        skill.run("add_card", deck="Q", front="What?", back="Answer")
        result = skill.run("quiz", deck="Q")
        assert "What?" in result

    def test_remove_card(self):
        skill = self._skill()
        skill.run("create_deck", deck="D")
        skill.run("add_card", deck="D", front="Q", back="A")
        result = skill.run("remove_card", deck="D", card_id=1)
        assert "Removed" in result

    def test_delete_deck(self):
        skill = self._skill()
        skill.run("create_deck", deck="Temp")
        result = skill.run("delete_deck", deck="Temp")
        assert "Deleted" in result

    def test_unknown_action(self):
        skill = self._skill()
        result = skill.run("flip")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# MorseCodeSkill
# ---------------------------------------------------------------------------

class TestMorseCodeSkill:
    from src.skills.morse_code import MorseCodeSkill
    skill = MorseCodeSkill()

    def test_encode_sos(self):
        result = self.skill.run("encode", text="SOS")
        assert "..." in result and "---" in result

    def test_decode_sos(self):
        result = self.skill.run("decode", text="... --- ...")
        assert "SOS" in result

    def test_encode_decode_round_trip(self):
        encoded = self.skill.run("encode", text="HELLO")
        decoded = self.skill.run("decode", text=encoded)
        assert "HELLO" in decoded

    def test_encode_numbers(self):
        result = self.skill.run("encode", text="42")
        # 4 = "....-" and 2 = "..---"
        assert "....-" in result and "..---" in result

    def test_missing_text(self):
        result = self.skill.run("encode")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("blink")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# AsciiArtSkill
# ---------------------------------------------------------------------------

class TestAsciiArtSkill:
    from src.skills.ascii_art import AsciiArtSkill
    skill = AsciiArtSkill()

    def test_banner(self):
        result = self.skill.run("banner", text="Hello")
        assert "Hello" in result and "┌" in result

    def test_box(self):
        result = self.skill.run("box", text="Test")
        assert "Test" in result and "│" in result

    def test_divider(self):
        result = self.skill.run("divider", char="-", width=20)
        assert result == "-" * 20

    def test_table(self):
        result = self.skill.run("table", text="Name|Age\nAlice|30\nBob|25")
        assert "Alice" in result and "Age" in result

    def test_progress_bar(self):
        result = self.skill.run("progress_bar", value=50, total=100, width=20)
        assert "50.0%" in result

    def test_bullet_list(self):
        result = self.skill.run("bullet_list", text="apples,oranges,grapes")
        assert "apples" in result and "•" in result

    def test_ascii_style_box(self):
        result = self.skill.run("box", text="Hello", style="ascii")
        assert "+" in result

    def test_missing_text(self):
        result = self.skill.run("banner")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("fireworks")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# ArchiveSkill
# ---------------------------------------------------------------------------

class TestArchiveSkill:
    from src.skills.archive_skill import ArchiveSkill

    def test_create_and_list_zip(self):
        skill = self.ArchiveSkill()
        # Create a temp file to archive
        src = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        src.write(b"hello")
        src.close()
        arch = src.name + ".zip"
        skill.run("create_zip", archive=arch, files=src.name)
        result = skill.run("list_zip", archive=arch)
        assert not result.startswith("Error:")
        assert os.path.basename(src.name) in result

    def test_extract_zip(self):
        skill = self.ArchiveSkill()
        src = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        src.write(b"data")
        src.close()
        arch = src.name + ".zip"
        skill.run("create_zip", archive=arch, files=src.name)
        dest = tempfile.mkdtemp()
        result = skill.run("extract_zip", archive=arch, dest=dest)
        assert "Extracted" in result

    def test_missing_archive(self):
        skill = self.ArchiveSkill()
        result = skill.run("list_zip")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        skill = self.ArchiveSkill()
        result = skill.run("compress")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# ContactsSkill
# ---------------------------------------------------------------------------

class TestContactsSkill:
    from src.skills.contacts_skill import ContactsSkill

    def _skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        return self.ContactsSkill(store_path=f.name)

    def test_add_contact(self):
        skill = self._skill()
        result = skill.run("add", name="Alice Smith", email="alice@example.com")
        assert "Alice Smith" in result

    def test_get_contact(self):
        skill = self._skill()
        skill.run("add", name="Bob Jones", phone="555-1234")
        result = skill.run("get", contact_id=1)
        assert "Bob Jones" in result

    def test_list_contacts(self):
        skill = self._skill()
        skill.run("add", name="Alice")
        skill.run("add", name="Bob")
        result = skill.run("list")
        assert "Alice" in result and "Bob" in result

    def test_update_contact(self):
        skill = self._skill()
        skill.run("add", name="Old Name")
        result = skill.run("update", contact_id=1, name="New Name")
        assert "Updated" in result

    def test_search_contact(self):
        skill = self._skill()
        skill.run("add", name="Carol Smith", email="carol@example.com")
        result = skill.run("search", query="carol")
        assert "Carol Smith" in result

    def test_delete_contact(self):
        skill = self._skill()
        skill.run("add", name="TempUser")
        result = skill.run("delete", contact_id=1)
        assert "Deleted" in result

    def test_clear(self):
        skill = self._skill()
        skill.run("add", name="A")
        result = skill.run("clear")
        assert "Cleared" in result

    def test_missing_name(self):
        skill = self._skill()
        result = skill.run("add")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        skill = self._skill()
        result = skill.run("export")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# NumberBaseSkill
# ---------------------------------------------------------------------------

class TestNumberBaseSkill:
    from src.skills.number_base import NumberBaseSkill
    skill = NumberBaseSkill()

    def test_to_binary(self):
        result = self.skill.run("to_binary", number="10")
        assert "1010" in result

    def test_to_octal(self):
        result = self.skill.run("to_octal", number="8")
        assert "10" in result

    def test_to_hex(self):
        result = self.skill.run("to_hex", number="255")
        assert "ff" in result.lower()

    def test_to_decimal_from_binary(self):
        result = self.skill.run("to_decimal", number="1010", from_base=2)
        assert "10" in result

    def test_convert(self):
        result = self.skill.run("convert", number="ff", from_base=16, to_base=10)
        assert "255" in result

    def test_table(self):
        result = self.skill.run("table", number="42")
        assert "Binary" in result and "Hexadecimal" in result

    def test_invalid_number(self):
        result = self.skill.run("to_decimal", number="xyz", from_base=10)
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("parse")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# CalendarSkill
# ---------------------------------------------------------------------------

class TestCalendarSkill:
    from src.skills.calendar_skill import CalendarSkill
    skill = CalendarSkill()

    def test_days_between(self):
        result = self.skill.run("days_between", date1="2025-01-01", date2="2025-01-10")
        assert "9" in result

    def test_add_days(self):
        result = self.skill.run("add_days", date="2025-01-01", days=7)
        assert result == "2025-01-08"

    def test_day_of_week(self):
        result = self.skill.run("day_of_week", date="2025-01-06")
        assert "Monday" in result

    def test_is_leap_year(self):
        result = self.skill.run("is_leap_year", year=2024)
        assert "is a leap year" in result

    def test_is_not_leap_year(self):
        result = self.skill.run("is_leap_year", year=2023)
        assert "is not" in result

    def test_month_calendar(self):
        result = self.skill.run("month_calendar", year=2025, month=1)
        assert "January" in result

    def test_next_weekday(self):
        result = self.skill.run("next_weekday", date="2025-01-06", weekday="Friday")
        assert "2025-01-10" in result

    def test_quarter(self):
        result = self.skill.run("quarter", date="2025-07-15")
        assert "Q3" in result

    def test_weeks_in_year(self):
        result = self.skill.run("weeks_in_year", year=2025)
        assert "week" in result

    def test_invalid_date(self):
        result = self.skill.run("day_of_week", date="not-a-date")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("predict")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# PomodoroSkill
# ---------------------------------------------------------------------------

class TestPomodoroSkill:
    from src.skills.pomodoro_skill import PomodoroSkill

    def _skill(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        return self.PomodoroSkill(store_path=f.name)

    def test_start_session(self):
        skill = self._skill()
        result = skill.run("start_session", task="Write code")
        assert "started" in result.lower()
        assert "Write code" in result

    def test_end_session(self):
        skill = self._skill()
        skill.run("start_session", task="Design")
        result = skill.run("end_session", session_id=1)
        assert "completed" in result.lower()

    def test_list_sessions(self):
        skill = self._skill()
        skill.run("start_session", task="Task A")
        result = skill.run("list_sessions")
        assert "Task A" in result

    def test_stats(self):
        skill = self._skill()
        skill.run("start_session", task="Coding")
        skill.run("end_session", session_id=1)
        result = skill.run("stats")
        assert "completed" in result.lower()

    def test_clear(self):
        skill = self._skill()
        skill.run("start_session", task="Misc")
        result = skill.run("clear")
        assert "Cleared" in result

    def test_missing_task(self):
        skill = self._skill()
        result = skill.run("start_session")
        assert result.startswith("Error:")

    def test_end_nonexistent_session(self):
        skill = self._skill()
        result = skill.run("end_session", session_id=99)
        assert result.startswith("Error:")

    def test_unknown_action(self):
        skill = self._skill()
        result = skill.run("sprint")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# CipherSkill
# ---------------------------------------------------------------------------

class TestCipherSkill:
    from src.skills.cipher_skill import CipherSkill
    skill = CipherSkill()

    def test_caesar_encode_decode(self):
        encoded = self.skill.run("caesar_encode", text="HELLO", shift=3)
        decoded = self.skill.run("caesar_decode", text=encoded, shift=3)
        assert decoded == "HELLO"

    def test_rot13_self_inverse(self):
        encoded = self.skill.run("rot13", text="Hello World")
        decoded = self.skill.run("rot13", text=encoded)
        assert decoded == "Hello World"

    def test_atbash(self):
        result = self.skill.run("atbash", text="ABC")
        assert result == "ZYX"

    def test_atbash_self_inverse(self):
        original = "Hello"
        encoded = self.skill.run("atbash", text=original)
        decoded = self.skill.run("atbash", text=encoded)
        assert decoded == original

    def test_vigenere_encode_decode(self):
        encoded = self.skill.run("vigenere_encode", text="HELLOWORLD", key="KEY")
        decoded = self.skill.run("vigenere_decode", text=encoded, key="KEY")
        assert decoded == "HELLOWORLD"

    def test_caesar_non_alpha_unchanged(self):
        result = self.skill.run("caesar_encode", text="Hello, World!", shift=1)
        assert "," in result and "!" in result

    def test_missing_text(self):
        result = self.skill.run("caesar_encode")
        assert result.startswith("Error:")

    def test_missing_key(self):
        result = self.skill.run("vigenere_encode", text="hello")
        assert result.startswith("Error:")

    def test_unknown_action(self):
        result = self.skill.run("xor")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# GitSkill (basic – only tests that don't require an actual git repo)
# ---------------------------------------------------------------------------

class TestGitSkill:
    from src.skills.git_skill import GitSkill
    skill = GitSkill()

    def test_unknown_action(self):
        result = self.skill.run("explode")
        assert result.startswith("Error:")

    def test_commit_requires_message(self):
        result = self.skill.run("commit", repo_path="/tmp")
        assert result.startswith("Error:")

    def test_checkout_requires_branch(self):
        result = self.skill.run("checkout", repo_path="/tmp")
        assert result.startswith("Error:")

    def test_init_real_dir(self):
        import shutil
        if not shutil.which("git"):
            return  # skip if git not installed
        d = tempfile.mkdtemp()
        result = self.skill.run("init", repo_path=d)
        assert not result.startswith("Error:")
