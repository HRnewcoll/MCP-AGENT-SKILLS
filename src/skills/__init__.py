"""Skill registry – import all skills and expose a unified registry."""

from .agent_swarm import AgentSwarmSkill
from .archive_skill import ArchiveSkill
from .ascii_art import AsciiArtSkill
from .base64_skill import Base64Skill
from .budget_tracker import BudgetTrackerSkill
from .calculator import CalculatorSkill
from .calendar_skill import CalendarSkill
from .cipher_skill import CipherSkill
from .code_executor import CodeExecutorSkill
from .color_converter import ColorConverterSkill
from .contacts_skill import ContactsSkill
from .csv_processor import CsvProcessorSkill
from .data_converter import DataConverterSkill
from .datetime_skill import DatetimeSkill
from .diff_tool import DiffToolSkill
from .disclawd import DisclawdSkill
from .file_manager import FileManagerSkill
from .flashcard_skill import FlashcardSkill
from .git_skill import GitSkill
from .hash_tool import HashToolSkill
from .http_request import HttpRequestSkill
from .json_processor import JsonProcessorSkill
from .markdown_skill import MarkdownSkill
from .memory import MemorySkill
from .morse_code import MorseCodeSkill
from .network_tools import NetworkToolsSkill
from .note_taker import NoteTakerSkill
from .number_base import NumberBaseSkill
from .password_generator import PasswordGeneratorSkill
from .pomodoro_skill import PomodoroSkill
from .random_generator import RandomGeneratorSkill
from .regex_tool import RegexToolSkill
from .shell_skill import ShellSkill
from .system_info import SystemInfoSkill
from .task_list import TaskListSkill
from .template_skill import TemplateSkill
from .text_processor import TextProcessorSkill
from .unit_converter import UnitConverterSkill
from .url_parser import UrlParserSkill
from .weather import WeatherSkill
from .web_search import WebSearchSkill
from .world_time import WorldTimeSkill

__all__ = [
    "AgentSwarmSkill",
    "ArchiveSkill",
    "AsciiArtSkill",
    "Base64Skill",
    "BudgetTrackerSkill",
    "CalculatorSkill",
    "CalendarSkill",
    "CipherSkill",
    "CodeExecutorSkill",
    "ColorConverterSkill",
    "ContactsSkill",
    "CsvProcessorSkill",
    "DataConverterSkill",
    "DatetimeSkill",
    "DiffToolSkill",
    "DisclawdSkill",
    "FileManagerSkill",
    "FlashcardSkill",
    "GitSkill",
    "HashToolSkill",
    "HttpRequestSkill",
    "JsonProcessorSkill",
    "MarkdownSkill",
    "MemorySkill",
    "MorseCodeSkill",
    "NetworkToolsSkill",
    "NoteTakerSkill",
    "NumberBaseSkill",
    "PasswordGeneratorSkill",
    "PomodoroSkill",
    "RandomGeneratorSkill",
    "RegexToolSkill",
    "ShellSkill",
    "SystemInfoSkill",
    "TaskListSkill",
    "TemplateSkill",
    "TextProcessorSkill",
    "UnitConverterSkill",
    "UrlParserSkill",
    "WeatherSkill",
    "WebSearchSkill",
    "WorldTimeSkill",
    "ALL_SKILLS",
]

# Ordered list of all available skill classes.
ALL_SKILLS = [
    AgentSwarmSkill,
    ArchiveSkill,
    AsciiArtSkill,
    Base64Skill,
    BudgetTrackerSkill,
    CalculatorSkill,
    CalendarSkill,
    CipherSkill,
    CodeExecutorSkill,
    ColorConverterSkill,
    ContactsSkill,
    CsvProcessorSkill,
    DataConverterSkill,
    DatetimeSkill,
    DiffToolSkill,
    DisclawdSkill,
    FileManagerSkill,
    FlashcardSkill,
    GitSkill,
    HashToolSkill,
    HttpRequestSkill,
    JsonProcessorSkill,
    MarkdownSkill,
    MemorySkill,
    MorseCodeSkill,
    NetworkToolsSkill,
    NoteTakerSkill,
    NumberBaseSkill,
    PasswordGeneratorSkill,
    PomodoroSkill,
    RandomGeneratorSkill,
    RegexToolSkill,
    ShellSkill,
    SystemInfoSkill,
    TaskListSkill,
    TemplateSkill,
    TextProcessorSkill,
    UnitConverterSkill,
    UrlParserSkill,
    WeatherSkill,
    WebSearchSkill,
    WorldTimeSkill,
]
