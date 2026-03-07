"""Tests for the 20 new skills added in this batch."""

import os
import tempfile

import pytest

from src.skills.nato_alphabet import NatoAlphabetSkill
from src.skills.loan_calculator import LoanCalculatorSkill
from src.skills.tip_calculator import TipCalculatorSkill
from src.skills.bmi_calculator import BmiCalculatorSkill
from src.skills.chart_skill import ChartSkill
from src.skills.dice_roller import DiceRollerSkill
from src.skills.joke_skill import JokeSkill
from src.skills.permutation_skill import PermutationSkill
from src.skills.matrix_skill import MatrixSkill
from src.skills.time_tracker import TimeTrackerSkill
from src.skills.reading_list import ReadingListSkill
from src.skills.quote_skill import QuoteSkill
from src.skills.sentiment_skill import SentimentSkill
from src.skills.table_formatter import TableFormatterSkill
from src.skills.fuzzy_match import FuzzyMatchSkill
from src.skills.finance_skill import FinanceSkill
from src.skills.color_palette import ColorPaletteSkill
from src.skills.poll_skill import PollSkill
from src.skills.currency_skill import CurrencySkill
from src.skills.emoji_skill import EmojiSkill


# ---------------------------------------------------------------------------
# NatoAlphabetSkill
# ---------------------------------------------------------------------------


class TestNatoAlphabetSkill:
    skill = NatoAlphabetSkill()

    def test_encode_simple(self):
        result = self.skill.run("encode", "AB")
        assert "Alpha" in result
        assert "Bravo" in result

    def test_encode_digits(self):
        result = self.skill.run("encode", "1")
        assert "One" in result

    def test_encode_space_separator(self):
        result = self.skill.run("encode", "A B")
        assert "/" in result

    def test_decode_simple(self):
        result = self.skill.run("decode", "Alpha Bravo")
        assert result == "AB"

    def test_decode_space_token(self):
        result = self.skill.run("decode", "Alpha / Bravo")
        assert " " in result

    def test_spell(self):
        result = self.skill.run("spell", "SOS")
        assert "Sierra" in result
        assert "Oscar" in result

    def test_empty_text_error(self):
        result = self.skill.run("encode", "")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("translate", "hello")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# LoanCalculatorSkill
# ---------------------------------------------------------------------------


class TestLoanCalculatorSkill:
    skill = LoanCalculatorSkill()

    def test_monthly_payment(self):
        result = self.skill.run("monthly_payment", principal=100000, annual_rate=5.0, years=30)
        assert "Monthly payment" in result
        assert "$" in result

    def test_total_interest(self):
        result = self.skill.run("total_interest", principal=100000, annual_rate=5.0, years=30)
        assert "Total interest" in result

    def test_zero_interest(self):
        result = self.skill.run("monthly_payment", principal=12000, annual_rate=0, years=1)
        assert "Monthly payment" in result
        assert "1,000" in result

    def test_amortize(self):
        result = self.skill.run("amortize", principal=100000, annual_rate=5.0, years=30, periods=3)
        assert "Period" in result
        assert "1" in result

    def test_compound_periods(self):
        result = self.skill.run("compound_periods", principal=1000, rate_per_period=0.05, target=2000)
        assert "Periods" in result

    def test_simple_interest(self):
        result = self.skill.run("simple_interest", principal=1000, annual_rate=10, years=2)
        assert "200" in result

    def test_apr_to_monthly(self):
        result = self.skill.run("apr_to_monthly", annual_rate=12.0)
        assert "Monthly rate" in result

    def test_bad_principal(self):
        result = self.skill.run("monthly_payment", principal=-100, annual_rate=5, years=10)
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# TipCalculatorSkill
# ---------------------------------------------------------------------------


class TestTipCalculatorSkill:
    skill = TipCalculatorSkill()

    def test_calculate_15_pct(self):
        result = self.skill.run("calculate", bill_amount=100, tip_percent=15)
        assert "15.00" in result
        assert "115.00" in result

    def test_split_between_4(self):
        result = self.skill.run("split", bill_amount=100, tip_percent=20, num_people=4)
        assert "Per person" in result
        assert "30.00" in result

    def test_recommend(self):
        result = self.skill.run("recommend", bill_amount=50)
        assert "15%" in result
        assert "20%" in result

    def test_custom_splits(self):
        result = self.skill.run("custom_splits", bill_amount=100, tip_percent=20, splits="50, 50")
        assert "60.00" in result

    def test_bad_bill(self):
        result = self.skill.run("calculate", bill_amount=-5)
        assert result.startswith("Error:")

    def test_bad_splits_sum(self):
        result = self.skill.run("custom_splits", bill_amount=100, tip_percent=15, splits="30, 30")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic", bill_amount=50)
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# BmiCalculatorSkill
# ---------------------------------------------------------------------------


class TestBmiCalculatorSkill:
    skill = BmiCalculatorSkill()

    def test_bmi_normal(self):
        result = self.skill.run("bmi", weight_kg=70, height_cm=175)
        assert "Normal weight" in result

    def test_bmi_underweight(self):
        result = self.skill.run("bmi", weight_kg=40, height_cm=175)
        assert "Underweight" in result

    def test_bmr_male(self):
        result = self.skill.run("bmr", weight_kg=80, height_cm=180, age=30, gender="male")
        assert "kcal" in result

    def test_bmr_female(self):
        result = self.skill.run("bmr", weight_kg=60, height_cm=165, age=25, gender="female")
        assert "kcal" in result

    def test_tdee(self):
        result = self.skill.run(
            "tdee", weight_kg=80, height_cm=180, age=30, gender="male", activity="moderate"
        )
        assert "TDEE" in result

    def test_ideal_weight(self):
        result = self.skill.run("ideal_weight", height_cm=175, gender="male")
        assert "Devine formula" in result

    def test_bmi_category_obese(self):
        result = self.skill.run("bmi_category", bmi_value=35)
        assert "Obese" in result

    def test_bad_weight(self):
        result = self.skill.run("bmi", weight_kg=0, height_cm=175)
        assert result.startswith("Error:")

    def test_bad_gender(self):
        result = self.skill.run("bmr", weight_kg=70, height_cm=170, age=25, gender="robot")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# ChartSkill
# ---------------------------------------------------------------------------


class TestChartSkill:
    skill = ChartSkill()

    def test_bar_chart(self):
        result = self.skill.run("bar", data="A:10,B:20,C:30")
        assert "█" in result
        assert "A" in result

    def test_bar_unlabeled(self):
        result = self.skill.run("bar", data="10,20,30")
        assert "█" in result

    def test_sparkline(self):
        result = self.skill.run("sparkline", data="1,2,3,4,5")
        assert len(result) == 5

    def test_histogram(self):
        data = ",".join(str(i) for i in range(100))
        result = self.skill.run("histogram", data=data, bins=5)
        assert "█" in result

    def test_pie_text(self):
        result = self.skill.run("pie_text", data="A:60,B:40")
        assert "60.0%" in result
        assert "40.0%" in result

    def test_missing_data(self):
        result = self.skill.run("bar", data="")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("scatter", data="1,2,3")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# DiceRollerSkill
# ---------------------------------------------------------------------------


class TestDiceRollerSkill:
    skill = DiceRollerSkill()

    def test_roll_1d6(self):
        result = self.skill.run("roll", expression="1d6")
        assert "🎲" in result
        # Total should be in 1..6
        total = int(result.split("=")[-1].strip())
        assert 1 <= total <= 6

    def test_roll_with_modifier(self):
        result = self.skill.run("roll", expression="1d6+10")
        total = int(result.split("=")[-1].strip())
        assert 11 <= total <= 16

    def test_roll_stats(self):
        result = self.skill.run("stats", expression="2d6")
        assert "Min" in result
        assert "Max" in result
        assert "Average" in result

    def test_roll_multiple(self):
        result = self.skill.run("roll_multiple", expression="1d6", times=5)
        assert "5 rolls" in result

    def test_fate(self):
        result = self.skill.run("fate")
        assert "Fate dice" in result

    def test_custom(self):
        result = self.skill.run("custom", faces="red,blue,green", count=3)
        assert "Custom die" in result

    def test_bad_expression(self):
        result = self.skill.run("roll", expression="bad")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# JokeSkill
# ---------------------------------------------------------------------------


class TestJokeSkill:
    skill = JokeSkill()

    def test_random_has_punchline(self):
        result = self.skill.run("random")
        assert "—" in result

    def test_by_category_programming(self):
        result = self.skill.run("by_category", category="programming")
        assert "—" in result

    def test_list_categories(self):
        result = self.skill.run("list_categories")
        assert "programming" in result

    def test_setup(self):
        result = self.skill.run("setup")
        assert result  # non-empty

    def test_pun(self):
        result = self.skill.run("pun")
        assert result  # non-empty

    def test_bad_category(self):
        result = self.skill.run("by_category", category="underwater_basketweaving")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# PermutationSkill
# ---------------------------------------------------------------------------


class TestPermutationSkill:
    skill = PermutationSkill()

    def test_permutations(self):
        result = self.skill.run("permutations", n=5, r=2)
        assert "P(5,2) = 20" in result

    def test_combinations(self):
        result = self.skill.run("combinations", n=5, r=2)
        assert "C(5,2) = 10" in result

    def test_factorial(self):
        result = self.skill.run("factorial", n=5)
        assert "120" in result

    def test_multinomial(self):
        result = self.skill.run("multinomial", values="2,3")
        assert "Multinomial" in result

    def test_derangements(self):
        result = self.skill.run("derangements", n=3)
        assert "D(3) = 2" in result

    def test_catalan(self):
        result = self.skill.run("catalan", n=4)
        assert "Catalan(4) = 14" in result

    def test_power_set_count(self):
        result = self.skill.run("power_set_count", n=4)
        assert result == "16"

    def test_list_permutations(self):
        result = self.skill.run("list_permutations", items="A,B,C")
        assert "6 permutation(s)" in result

    def test_list_combinations(self):
        result = self.skill.run("list_combinations", items="A,B,C,D", r=2)
        assert "6 combination(s)" in result

    def test_r_greater_than_n(self):
        result = self.skill.run("permutations", n=3, r=5)
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# MatrixSkill
# ---------------------------------------------------------------------------


class TestMatrixSkill:
    skill = MatrixSkill()

    def test_add(self):
        result = self.skill.run("add", matrix_a="1,2;3,4", matrix_b="5,6;7,8")
        assert "6" in result
        assert "8" in result
        assert "10" in result
        assert "12" in result

    def test_multiply_identity(self):
        result = self.skill.run("multiply", matrix_a="1,2;3,4", matrix_b="1,0;0,1")
        assert "1" in result
        assert "4" in result

    def test_transpose(self):
        result = self.skill.run("transpose", matrix_a="1,2,3;4,5,6")
        # After transposing 2x3 becomes 3x2
        assert "1" in result
        assert "4" in result

    def test_determinant_2x2(self):
        result = self.skill.run("determinant", matrix_a="1,2;3,4")
        assert "det = -2" in result

    def test_identity_3x3(self):
        result = self.skill.run("identity", n=3)
        assert "1" in result

    def test_scalar_multiply(self):
        result = self.skill.run("scalar_multiply", matrix_a="1,2;3,4", scalar=2)
        assert "8" in result

    def test_trace(self):
        result = self.skill.run("trace", matrix_a="1,2;3,4")
        assert "trace = 5" in result

    def test_incompatible_dimensions(self):
        result = self.skill.run("multiply", matrix_a="1,2,3;4,5,6", matrix_b="1,2;3,4")
        assert result.startswith("Error:")

    def test_missing_matrix(self):
        result = self.skill.run("add", matrix_a="1,2;3,4")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("inverse")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# TimeTrackerSkill
# ---------------------------------------------------------------------------


class TestTimeTrackerSkill:
    def setup_method(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)
        self.path = path
        self.skill = TimeTrackerSkill(store_path=path)

    def teardown_method(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_log_and_list(self):
        self.skill.run("log", task="coding", minutes=60)
        result = self.skill.run("list")
        assert "coding" in result

    def test_summary(self):
        self.skill.run("log", task="coding", minutes=60)
        self.skill.run("log", task="meeting", minutes=30)
        result = self.skill.run("summary")
        assert "coding" in result
        assert "meeting" in result

    def test_start_stop(self):
        self.skill.run("start", task="reading")
        result = self.skill.run("running")
        assert "reading" in result
        result = self.skill.run("stop", task="reading")
        assert "Stopped" in result

    def test_cannot_start_twice(self):
        self.skill.run("start", task="reading")
        result = self.skill.run("start", task="reading")
        assert "already running" in result

    def test_delete(self):
        self.skill.run("log", task="coding", minutes=10)
        result = self.skill.run("list")
        entry_id = int(result.split("#")[1].split()[0])
        result = self.skill.run("delete", entry_id=entry_id)
        assert "Deleted" in result

    def test_clear(self):
        self.skill.run("log", task="coding", minutes=10)
        result = self.skill.run("clear")
        assert "Cleared" in result

    def test_missing_task(self):
        result = self.skill.run("log", minutes=10)
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# ReadingListSkill
# ---------------------------------------------------------------------------


class TestReadingListSkill:
    def setup_method(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)
        self.path = path
        self.skill = ReadingListSkill(store_path=path)

    def teardown_method(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_add_and_list(self):
        self.skill.run("add", title="Dune", author="Frank Herbert")
        result = self.skill.run("list", status="all")
        assert "Dune" in result

    def test_list_filter_want_to_read(self):
        self.skill.run("add", title="Dune", author="Herbert")
        # Default status is want_to_read; filtering on it should return the book
        result = self.skill.run("list", status="want_to_read")
        assert "Dune" in result

    def test_update_status(self):
        self.skill.run("add", title="1984", author="Orwell")
        result = self.skill.run("list", status="all")
        book_id = int(result.split("#")[1].split()[0])
        result = self.skill.run("update_status", book_id=book_id, status="read")
        assert "Updated" in result

    def test_rate(self):
        self.skill.run("add", title="Dune", author="Herbert")
        result = self.skill.run("list", status="all")
        book_id = int(result.split("#")[1].split()[0])
        result = self.skill.run("rate", book_id=book_id, rating=5)
        assert "★★★★★" in result

    def test_note(self):
        self.skill.run("add", title="Dune", author="Herbert")
        result = self.skill.run("list", status="all")
        book_id = int(result.split("#")[1].split()[0])
        result = self.skill.run("note", book_id=book_id, text="Great book!")
        assert "Note saved" in result

    def test_search(self):
        self.skill.run("add", title="Dune", author="Herbert")
        result = self.skill.run("search", query="dune")
        assert "1 result" in result

    def test_stats(self):
        self.skill.run("add", title="Dune", author="Herbert")
        result = self.skill.run("stats")
        assert "Total books" in result

    def test_delete(self):
        self.skill.run("add", title="Dune", author="Herbert")
        result = self.skill.run("list", status="all")
        book_id = int(result.split("#")[1].split()[0])
        result = self.skill.run("delete", book_id=book_id)
        assert "Deleted" in result

    def test_bad_rating(self):
        self.skill.run("add", title="Dune", author="Herbert")
        result = self.skill.run("list", status="all")
        book_id = int(result.split("#")[1].split()[0])
        result = self.skill.run("rate", book_id=book_id, rating=6)
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# QuoteSkill
# ---------------------------------------------------------------------------


class TestQuoteSkill:
    def setup_method(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)
        self.path = path
        self.skill = QuoteSkill(store_path=path)

    def teardown_method(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_random(self):
        result = self.skill.run("random")
        assert '"' in result
        assert "—" in result

    def test_by_author(self):
        result = self.skill.run("by_author", author="Einstein")
        assert "Einstein" in result

    def test_search(self):
        result = self.skill.run("search", query="dream")
        assert "quote" in result.lower()

    def test_add_and_list_custom(self):
        self.skill.run("add", text="Be the change.", author="Gandhi")
        result = self.skill.run("list_custom")
        assert "Gandhi" in result

    def test_list_authors(self):
        result = self.skill.run("list_authors")
        assert "Einstein" in result

    def test_daily(self):
        result = self.skill.run("daily")
        assert '"' in result

    def test_delete_custom(self):
        self.skill.run("add", text="Custom quote", author="Test Author")
        result = self.skill.run("list_custom")
        quote_id = int(result.split("#")[1].split()[0])
        result = self.skill.run("delete", quote_id=quote_id)
        assert "Deleted" in result

    def test_bad_by_author(self):
        result = self.skill.run("by_author", author="Nonexistent Person XXXX")
        assert "No quotes found" in result

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# SentimentSkill
# ---------------------------------------------------------------------------


class TestSentimentSkill:
    skill = SentimentSkill()

    def test_positive_text(self):
        result = self.skill.run("analyze", text="I love this, it is amazing and wonderful!")
        assert "positive" in result

    def test_negative_text(self):
        result = self.skill.run("analyze", text="This is terrible and awful and bad.")
        assert "negative" in result

    def test_score_positive(self):
        result = self.skill.run("score", text="great excellent wonderful")
        score = float(result)
        assert score > 0

    def test_score_negative(self):
        result = self.skill.run("score", text="terrible awful horrible")
        score = float(result)
        assert score < 0

    def test_words(self):
        result = self.skill.run("words", text="I love good things but hate bad ones")
        assert "Positive words" in result
        assert "Negative words" in result

    def test_compare(self):
        result = self.skill.run(
            "compare",
            text="This is great",
            text2="This is terrible",
        )
        assert "Text 1" in result
        assert "Text 2" in result

    def test_missing_text(self):
        result = self.skill.run("analyze", text="")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic", text="hello")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# TableFormatterSkill
# ---------------------------------------------------------------------------


class TestTableFormatterSkill:
    skill = TableFormatterSkill()

    def test_ascii_table(self):
        result = self.skill.run("ascii", data="Name,Age;Alice,30;Bob,25")
        assert "Name" in result
        assert "Alice" in result
        assert "Bob" in result
        assert "|" in result

    def test_markdown_table(self):
        result = self.skill.run("markdown", data="Name,Age;Alice,30;Bob,25")
        assert "|" in result
        assert "Name" in result

    def test_csv_to_table(self):
        result = self.skill.run("csv_to_table", data="Name,Age\nAlice,30\nBob,25")
        assert "Alice" in result

    def test_json_to_table(self):
        import json
        data = json.dumps([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])
        result = self.skill.run("json_to_table", data=data)
        assert "Alice" in result
        assert "name" in result

    def test_transpose(self):
        result = self.skill.run("transpose", data="A,B;1,2;3,4")
        assert "A" in result
        assert "1" in result

    def test_missing_data(self):
        result = self.skill.run("ascii", data="")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("html", data="Name,Age;Alice,30")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# FuzzyMatchSkill
# ---------------------------------------------------------------------------


class TestFuzzyMatchSkill:
    skill = FuzzyMatchSkill()

    def test_distance_identical(self):
        assert self.skill.run("distance", s1="hello", s2="hello") == "0"

    def test_distance_one_edit(self):
        assert self.skill.run("distance", s1="hello", s2="helo") == "1"

    def test_similarity_identical(self):
        result = float(self.skill.run("similarity", s1="hello", s2="hello"))
        assert result == 1.0

    def test_similarity_partial(self):
        result = float(self.skill.run("similarity", s1="hello", s2="world"))
        assert 0.0 <= result < 1.0

    def test_best_match(self):
        result = self.skill.run(
            "best_match", query="hello", candidates="helo,world,hello world,hi"
        )
        assert "helo" in result or "hello" in result

    def test_rank_matches(self):
        result = self.skill.run(
            "rank_matches", query="python", candidates="python,ruby,perl,java"
        )
        assert "python" in result
        assert "1." in result

    def test_jaro(self):
        result = float(self.skill.run("jaro", s1="MARTHA", s2="MARHTA"))
        assert result > 0.9

    def test_jaro_winkler(self):
        result = float(self.skill.run("jaro_winkler", s1="MARTHA", s2="MARHTA"))
        assert result > 0.9

    def test_missing_strings(self):
        result = self.skill.run("distance", s1="", s2="hello")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic", s1="a", s2="b")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# FinanceSkill
# ---------------------------------------------------------------------------


class TestFinanceSkill:
    skill = FinanceSkill()

    def test_compound_interest(self):
        result = self.skill.run("compound_interest", principal=1000, annual_rate=5, years=10)
        assert "Future value" in result
        assert "1,647" in result or "1647" in result

    def test_future_value(self):
        result = self.skill.run("future_value", payment=100, annual_rate=6, years=5)
        assert "Future value" in result

    def test_present_value(self):
        result = self.skill.run("present_value", future_amount=1000, annual_rate=5, years=5)
        assert "Present value" in result

    def test_roi_positive(self):
        result = self.skill.run("roi", initial_investment=1000, final_value=1500)
        assert "50.00%" in result

    def test_roi_negative(self):
        result = self.skill.run("roi", initial_investment=1000, final_value=800)
        assert "-20.00%" in result

    def test_npv(self):
        result = self.skill.run("npv", rate=10, cash_flows="-1000,300,400,500")
        assert "NPV" in result

    def test_break_even(self):
        result = self.skill.run("break_even", fixed_cost=1000, price_per_unit=20, variable_cost_per_unit=10)
        assert "100 unit" in result

    def test_savings_goal(self):
        result = self.skill.run("savings_goal", goal=12000, monthly_deposit=100, annual_rate=5)
        assert "Time to goal" in result

    def test_inflation_adjust(self):
        result = self.skill.run("inflation_adjust", amount=100, annual_inflation=3, years=10)
        assert "Equivalent cost" in result

    def test_bad_principal(self):
        result = self.skill.run("compound_interest", principal=-100, annual_rate=5, years=10)
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# ColorPaletteSkill
# ---------------------------------------------------------------------------


class TestColorPaletteSkill:
    skill = ColorPaletteSkill()

    def test_complementary(self):
        result = self.skill.run("complementary", hex_color="#FF0000")
        assert "180" in result and "°" in result

    def test_analogous(self):
        result = self.skill.run("analogous", hex_color="#FF0000")
        assert "Base" in result

    def test_triadic(self):
        result = self.skill.run("triadic", hex_color="#FF0000")
        assert "120" in result and "°" in result

    def test_shades(self):
        result = self.skill.run("shades", hex_color="#3366CC", count=5)
        assert "#" in result
        lines = [l for l in result.splitlines() if l.strip()]
        assert len(lines) == 5

    def test_hex_to_rgb(self):
        result = self.skill.run("hex_to_rgb", hex_color="#FF0000")
        assert "rgb(255, 0, 0)" in result

    def test_rgb_to_hex(self):
        result = self.skill.run("rgb_to_hex", r=255, g=0, b=0)
        assert "#FF0000" in result

    def test_rgb_to_hsl(self):
        result = self.skill.run("rgb_to_hsl", r=255, g=0, b=0)
        assert "hsl(" in result

    def test_hsl_to_rgb(self):
        result = self.skill.run("hsl_to_rgb", hue=0, saturation=100, lightness=50)
        assert "rgb(" in result

    def test_bad_hex(self):
        result = self.skill.run("hex_to_rgb", hex_color="ZZZZZZ")
        assert result.startswith("Error:")

    def test_missing_hex(self):
        result = self.skill.run("complementary", hex_color="")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# PollSkill
# ---------------------------------------------------------------------------


class TestPollSkill:
    def setup_method(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(path)
        self.path = path
        self.skill = PollSkill(store_path=path)

    def teardown_method(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_create_and_list(self):
        self.skill.run("create", question="Best language?", options="Python,Java,Go")
        result = self.skill.run("list")
        assert "Best language?" in result

    def test_vote_and_results(self):
        self.skill.run("create", question="Best?", options="A,B,C")
        result = self.skill.run("list")
        poll_id = int(result.split("#")[1].split()[0])
        self.skill.run("vote", poll_id=poll_id, option="A")
        result = self.skill.run("results", poll_id=poll_id)
        assert "A" in result
        assert "1 vote" in result

    def test_vote_by_number(self):
        self.skill.run("create", question="Best?", options="A,B,C")
        result = self.skill.run("list")
        poll_id = int(result.split("#")[1].split()[0])
        self.skill.run("vote", poll_id=poll_id, option="2")
        result = self.skill.run("results", poll_id=poll_id)
        assert "B" in result

    def test_close(self):
        self.skill.run("create", question="Best?", options="A,B")
        result = self.skill.run("list")
        poll_id = int(result.split("#")[1].split()[0])
        self.skill.run("close", poll_id=poll_id)
        result = self.skill.run("vote", poll_id=poll_id, option="A")
        assert result.startswith("Error:")

    def test_delete(self):
        self.skill.run("create", question="Best?", options="A,B")
        result = self.skill.run("list")
        poll_id = int(result.split("#")[1].split()[0])
        result = self.skill.run("delete", poll_id=poll_id)
        assert "Deleted" in result

    def test_clear(self):
        self.skill.run("create", question="Best?", options="A,B")
        result = self.skill.run("clear")
        assert "Cleared" in result

    def test_bad_options(self):
        result = self.skill.run("create", question="Best?", options="OnlyOne")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# CurrencySkill
# ---------------------------------------------------------------------------


class TestCurrencySkill:
    skill = CurrencySkill()

    def test_convert_usd_to_eur(self):
        result = self.skill.run("convert", amount=100, from_currency="USD", to_currency="EUR")
        assert "USD" in result
        assert "EUR" in result

    def test_convert_same_currency(self):
        result = self.skill.run("convert", amount=100, from_currency="USD", to_currency="USD")
        assert "100.0000 USD" in result

    def test_list_currencies(self):
        result = self.skill.run("list_currencies")
        assert "USD" in result
        assert "EUR" in result
        assert "JPY" in result

    def test_rate(self):
        result = self.skill.run("rate", from_currency="USD", to_currency="GBP")
        assert "1 USD" in result
        assert "GBP" in result

    def test_compare(self):
        result = self.skill.run("compare", amount=100, from_currency="USD", to_currencies="EUR,GBP,JPY")
        assert "EUR" in result
        assert "JPY" in result

    def test_bad_currency(self):
        result = self.skill.run("convert", amount=100, from_currency="XYZ", to_currency="USD")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# EmojiSkill
# ---------------------------------------------------------------------------


class TestEmojiSkill:
    skill = EmojiSkill()

    def test_find(self):
        result = self.skill.run("find", query="cat")
        assert "🐱" in result

    def test_find_no_results(self):
        result = self.skill.run("find", query="xyzxyzxyz_unknown_thing")
        assert "No emoji" in result

    def test_random(self):
        result = self.skill.run("random")
        assert result  # non-empty

    def test_list_categories(self):
        result = self.skill.run("list_categories")
        assert "faces" in result
        assert "animals" in result

    def test_by_category(self):
        result = self.skill.run("by_category", category="food")
        assert "🍕" in result

    def test_by_bad_category(self):
        result = self.skill.run("by_category", category="nonexistent_xyz")
        assert result.startswith("Error:") or "No emoji" in result

    def test_info(self):
        result = self.skill.run("info", name="pizza")
        assert "🍕" in result
        assert "Category" in result

    def test_find_missing_query(self):
        result = self.skill.run("find", query="")
        assert result.startswith("Error:")

    def test_unknown_action_error(self):
        result = self.skill.run("magic")
        assert result.startswith("Error:")
