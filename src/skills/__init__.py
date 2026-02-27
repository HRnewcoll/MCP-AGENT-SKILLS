"""Skill registry – import all skills and expose a unified registry."""

from .calculator import CalculatorSkill
from .code_executor import CodeExecutorSkill
from .file_manager import FileManagerSkill
from .memory import MemorySkill
from .weather import WeatherSkill
from .web_search import WebSearchSkill

__all__ = [
    "CalculatorSkill",
    "CodeExecutorSkill",
    "FileManagerSkill",
    "MemorySkill",
    "WeatherSkill",
    "WebSearchSkill",
    "ALL_SKILLS",
]

# Ordered list of all available skill classes.
ALL_SKILLS = [
    CalculatorSkill,
    CodeExecutorSkill,
    FileManagerSkill,
    MemorySkill,
    WeatherSkill,
    WebSearchSkill,
]
