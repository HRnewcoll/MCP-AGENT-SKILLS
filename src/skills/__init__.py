"""Skill registry – import all skills and expose a unified registry."""

from .calculator import CalculatorSkill
from .code_executor import CodeExecutorSkill
from .data_converter import DataConverterSkill
from .datetime_skill import DatetimeSkill
from .diff_tool import DiffToolSkill
from .file_manager import FileManagerSkill
from .hash_tool import HashToolSkill
from .http_request import HttpRequestSkill
from .json_processor import JsonProcessorSkill
from .memory import MemorySkill
from .note_taker import NoteTakerSkill
from .random_generator import RandomGeneratorSkill
from .regex_tool import RegexToolSkill
from .shell_skill import ShellSkill
from .system_info import SystemInfoSkill
from .task_list import TaskListSkill
from .text_processor import TextProcessorSkill
from .unit_converter import UnitConverterSkill
from .weather import WeatherSkill
from .web_search import WebSearchSkill

__all__ = [
    "CalculatorSkill",
    "CodeExecutorSkill",
    "DataConverterSkill",
    "DatetimeSkill",
    "DiffToolSkill",
    "FileManagerSkill",
    "HashToolSkill",
    "HttpRequestSkill",
    "JsonProcessorSkill",
    "MemorySkill",
    "NoteTakerSkill",
    "RandomGeneratorSkill",
    "RegexToolSkill",
    "ShellSkill",
    "SystemInfoSkill",
    "TaskListSkill",
    "TextProcessorSkill",
    "UnitConverterSkill",
    "WeatherSkill",
    "WebSearchSkill",
    "ALL_SKILLS",
]

# Ordered list of all available skill classes.
ALL_SKILLS = [
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
]
