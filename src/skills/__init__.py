"""Skill registry – import all skills and expose a unified registry."""

from .agent_swarm import AgentSwarmSkill
from .anagram_skill import AnagramSkill
from .bmi_calculator import BmiCalculatorSkill
from .chart_skill import ChartSkill
from .color_palette import ColorPaletteSkill
from .currency_skill import CurrencySkill
from .dice_roller import DiceRollerSkill
from .emoji_skill import EmojiSkill
from .finance_skill import FinanceSkill
from .fuzzy_match import FuzzyMatchSkill
from .joke_skill import JokeSkill
from .loan_calculator import LoanCalculatorSkill
from .matrix_skill import MatrixSkill
from .nato_alphabet import NatoAlphabetSkill
from .permutation_skill import PermutationSkill
from .poll_skill import PollSkill
from .quote_skill import QuoteSkill
from .reading_list import ReadingListSkill
from .sentiment_skill import SentimentSkill
from .table_formatter import TableFormatterSkill
from .time_tracker import TimeTrackerSkill
from .tip_calculator import TipCalculatorSkill
from .archive_skill import ArchiveSkill
from .ascii_art import AsciiArtSkill
from .base64_skill import Base64Skill
from .bookmark_skill import BookmarkSkill
from .budget_tracker import BudgetTrackerSkill
from .calculator import CalculatorSkill
from .calendar_skill import CalendarSkill
from .cipher_skill import CipherSkill
from .code_executor import CodeExecutorSkill
from .color_converter import ColorConverterSkill
from .contacts_skill import ContactsSkill
from .countdown_skill import CountdownSkill
from .cron_parser import CronParserSkill
from .csv_processor import CsvProcessorSkill
from .data_converter import DataConverterSkill
from .datetime_skill import DatetimeSkill
from .diary_skill import DiarySkill
from .diff_tool import DiffToolSkill
from .disclawd import DisclawdSkill
from .email_validator import EmailValidatorSkill
from .file_manager import FileManagerSkill
from .flashcard_skill import FlashcardSkill
from .git_skill import GitSkill
from .habit_tracker import HabitTrackerSkill
from .hash_tool import HashToolSkill
from .http_request import HttpRequestSkill
from .ini_config import IniConfigSkill
from .ip_address_skill import IpAddressSkill
from .json_processor import JsonProcessorSkill
from .leaderboard_skill import LeaderboardSkill
from .markdown_skill import MarkdownSkill
from .math_sequence import MathSequenceSkill
from .memory import MemorySkill
from .mind_map_skill import MindMapSkill
from .morse_code import MorseCodeSkill
from .network_tools import NetworkToolsSkill
from .note_taker import NoteTakerSkill
from .number_base import NumberBaseSkill
from .palindrome_skill import PalindromeSkill
from .password_generator import PasswordGeneratorSkill
from .pomodoro_skill import PomodoroSkill
from .random_generator import RandomGeneratorSkill
from .regex_tool import RegexToolSkill
from .roman_numeral import RomanNumeralSkill
from .shell_skill import ShellSkill
from .speed_reading import SpeedReadingSkill
from .sqlite_skill import SqliteSkill
from .statistics_skill import StatisticsSkill
from .system_info import SystemInfoSkill
from .task_list import TaskListSkill
from .template_skill import TemplateSkill
from .text_processor import TextProcessorSkill
from .typing_speed import TypingSpeedSkill
from .unit_converter import UnitConverterSkill
from .url_parser import UrlParserSkill
from .weather import WeatherSkill
from .web_search import WebSearchSkill
from .word_frequency import WordFrequencySkill
from .world_time import WorldTimeSkill
from .workout_tracker import WorkoutTrackerSkill

__all__ = [
    "AgentSwarmSkill",
    "AnagramSkill",
    "BmiCalculatorSkill",
    "ChartSkill",
    "ColorPaletteSkill",
    "CurrencySkill",
    "DiceRollerSkill",
    "EmojiSkill",
    "FinanceSkill",
    "FuzzyMatchSkill",
    "JokeSkill",
    "LoanCalculatorSkill",
    "MatrixSkill",
    "NatoAlphabetSkill",
    "PermutationSkill",
    "PollSkill",
    "QuoteSkill",
    "ReadingListSkill",
    "SentimentSkill",
    "TableFormatterSkill",
    "TimeTrackerSkill",
    "TipCalculatorSkill",
    "ArchiveSkill",
    "AsciiArtSkill",
    "Base64Skill",
    "BookmarkSkill",
    "BudgetTrackerSkill",
    "CalculatorSkill",
    "CalendarSkill",
    "CipherSkill",
    "CodeExecutorSkill",
    "ColorConverterSkill",
    "ContactsSkill",
    "CountdownSkill",
    "CronParserSkill",
    "CsvProcessorSkill",
    "DataConverterSkill",
    "DatetimeSkill",
    "DiarySkill",
    "DiffToolSkill",
    "DisclawdSkill",
    "EmailValidatorSkill",
    "FileManagerSkill",
    "FlashcardSkill",
    "GitSkill",
    "HabitTrackerSkill",
    "HashToolSkill",
    "HttpRequestSkill",
    "IniConfigSkill",
    "IpAddressSkill",
    "JsonProcessorSkill",
    "LeaderboardSkill",
    "MarkdownSkill",
    "MathSequenceSkill",
    "MemorySkill",
    "MindMapSkill",
    "MorseCodeSkill",
    "NetworkToolsSkill",
    "NoteTakerSkill",
    "NumberBaseSkill",
    "PalindromeSkill",
    "PasswordGeneratorSkill",
    "PomodoroSkill",
    "RandomGeneratorSkill",
    "RegexToolSkill",
    "RomanNumeralSkill",
    "ShellSkill",
    "SpeedReadingSkill",
    "SqliteSkill",
    "StatisticsSkill",
    "SystemInfoSkill",
    "TaskListSkill",
    "TemplateSkill",
    "TextProcessorSkill",
    "TypingSpeedSkill",
    "UnitConverterSkill",
    "UrlParserSkill",
    "WeatherSkill",
    "WebSearchSkill",
    "WordFrequencySkill",
    "WorldTimeSkill",
    "WorkoutTrackerSkill",
    "ALL_SKILLS",
]

# Ordered list of all available skill classes.
ALL_SKILLS = [
    AgentSwarmSkill,
    AnagramSkill,
    BmiCalculatorSkill,
    ChartSkill,
    ColorPaletteSkill,
    CurrencySkill,
    DiceRollerSkill,
    EmojiSkill,
    FinanceSkill,
    FuzzyMatchSkill,
    JokeSkill,
    LoanCalculatorSkill,
    MatrixSkill,
    NatoAlphabetSkill,
    PermutationSkill,
    PollSkill,
    QuoteSkill,
    ReadingListSkill,
    SentimentSkill,
    TableFormatterSkill,
    TimeTrackerSkill,
    TipCalculatorSkill,
    ArchiveSkill,
    AsciiArtSkill,
    Base64Skill,
    BookmarkSkill,
    BudgetTrackerSkill,
    CalculatorSkill,
    CalendarSkill,
    CipherSkill,
    CodeExecutorSkill,
    ColorConverterSkill,
    ContactsSkill,
    CountdownSkill,
    CronParserSkill,
    CsvProcessorSkill,
    DataConverterSkill,
    DatetimeSkill,
    DiarySkill,
    DiffToolSkill,
    DisclawdSkill,
    EmailValidatorSkill,
    FileManagerSkill,
    FlashcardSkill,
    GitSkill,
    HabitTrackerSkill,
    HashToolSkill,
    HttpRequestSkill,
    IniConfigSkill,
    IpAddressSkill,
    JsonProcessorSkill,
    LeaderboardSkill,
    MarkdownSkill,
    MathSequenceSkill,
    MemorySkill,
    MindMapSkill,
    MorseCodeSkill,
    NetworkToolsSkill,
    NoteTakerSkill,
    NumberBaseSkill,
    PalindromeSkill,
    PasswordGeneratorSkill,
    PomodoroSkill,
    RandomGeneratorSkill,
    RegexToolSkill,
    RomanNumeralSkill,
    ShellSkill,
    SpeedReadingSkill,
    SqliteSkill,
    StatisticsSkill,
    SystemInfoSkill,
    TaskListSkill,
    TemplateSkill,
    TextProcessorSkill,
    TypingSpeedSkill,
    UnitConverterSkill,
    UrlParserSkill,
    WeatherSkill,
    WebSearchSkill,
    WordFrequencySkill,
    WorldTimeSkill,
    WorkoutTrackerSkill,
]
