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
