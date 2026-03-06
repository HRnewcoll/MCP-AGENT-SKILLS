"""Speed reading skill – estimate reading time and reading level for text.

Covers the "Personal Development" and "Productivity & Tasks" categories.
Uses Python stdlib only.

Supported actions
-----------------
reading_time    Estimate time to read a piece of text.
word_stats      Return word/sentence/paragraph statistics.
reading_level   Estimate Flesch-Kincaid reading ease and grade level.
summarize_stats Return a full summary report for the text.
"""

from __future__ import annotations

import re


# Average words per minute for different reading modes
_WPM = {
    "slow": 150,
    "average": 238,
    "fast": 400,
    "skimming": 700,
}

# Syllable counting helper
def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:'\"()")
    if not word:
        return 0
    # Simple heuristic
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and not word.endswith("le") and count > 1:
        count -= 1
    return max(1, count)


class SpeedReadingSkill:
    """Estimate reading time and reading level for text."""

    name = "speed_reading"
    description = (
        "Analyse text for reading time and complexity. "
        "Supported actions: 'reading_time' (text, speed=average); "
        "'word_stats' (text); 'reading_level' (text); "
        "'summarize_stats' (text)."
        "\nspeed options: slow (150 wpm), average (238 wpm), "
        "fast (400 wpm), skimming (700 wpm)."
    )

    def run(
        self,
        action: str,
        text: str = "",
        speed: str = "average",
    ) -> str:
        """
        Analyse text for reading metrics.

        Parameters
        ----------
        action:
            One of ``"reading_time"``, ``"word_stats"``,
            ``"reading_level"``, ``"summarize_stats"``.
        text:
            The text to analyse.
        speed:
            Reading speed preset for ``"reading_time"``
            (slow/average/fast/skimming, default ``"average"``).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if not text and action != "reading_time":
            return "Error: text is required"

        if action == "reading_time":
            return self._reading_time(text, speed)
        if action == "word_stats":
            return self._word_stats(text)
        if action == "reading_level":
            return self._reading_level(text)
        if action == "summarize_stats":
            return self._summarize(text, speed)
        return (
            f"Error: unknown action {action!r}. "
            "Use reading_time, word_stats, reading_level, or summarize_stats."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _word_count(text: str) -> int:
        return len(text.split())

    @staticmethod
    def _sentence_count(text: str) -> int:
        sentences = re.split(r"[.!?]+", text)
        return max(1, sum(1 for s in sentences if s.strip()))

    @staticmethod
    def _paragraph_count(text: str) -> int:
        paragraphs = re.split(r"\n{2,}", text.strip())
        return max(1, sum(1 for p in paragraphs if p.strip()))

    def _reading_time(self, text: str, speed: str) -> str:
        if not text:
            return "Error: text is required"
        wpm = _WPM.get(speed.lower(), _WPM["average"])
        words = self._word_count(text)
        total_sec = (words / wpm) * 60
        minutes = int(total_sec // 60)
        seconds = int(total_sec % 60)
        return (
            f"Words: {words}  Speed: {wpm} wpm ({speed})\n"
            f"Reading time: {minutes}m {seconds}s"
        )

    def _word_stats(self, text: str) -> str:
        words = self._word_count(text)
        chars = len(text)
        chars_no_spaces = len(text.replace(" ", "").replace("\n", ""))
        sentences = self._sentence_count(text)
        paragraphs = self._paragraph_count(text)
        avg_wps = round(words / sentences, 1) if sentences else 0
        return (
            f"Characters     : {chars}\n"
            f"Chars (no space): {chars_no_spaces}\n"
            f"Words          : {words}\n"
            f"Sentences      : {sentences}\n"
            f"Paragraphs     : {paragraphs}\n"
            f"Avg words/sent : {avg_wps}"
        )

    def _reading_level(self, text: str) -> str:
        words_list = re.findall(r"\b[a-zA-Z]+\b", text)
        if not words_list:
            return "Error: no words found in text"
        words = len(words_list)
        sentences = max(1, self._sentence_count(text))
        syllables = sum(_count_syllables(w) for w in words_list)

        # Flesch Reading Ease
        ease = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        ease = max(0.0, min(100.0, ease))

        # Flesch-Kincaid Grade Level
        grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59

        if ease >= 90:
            level_desc = "Very easy (5th grade)"
        elif ease >= 80:
            level_desc = "Easy (6th grade)"
        elif ease >= 70:
            level_desc = "Fairly easy (7th grade)"
        elif ease >= 60:
            level_desc = "Standard (8th-9th grade)"
        elif ease >= 50:
            level_desc = "Fairly difficult (10th-12th grade)"
        elif ease >= 30:
            level_desc = "Difficult (college)"
        else:
            level_desc = "Very difficult (professional)"

        return (
            f"Flesch Reading Ease  : {ease:.1f}/100 – {level_desc}\n"
            f"FK Grade Level       : {grade:.1f}\n"
            f"Words                : {words}\n"
            f"Sentences            : {sentences}\n"
            f"Syllables            : {syllables}\n"
            f"Avg syllables/word   : {syllables / words:.2f}"
        )

    def _summarize(self, text: str, speed: str) -> str:
        parts = [
            "=== Reading Summary ===",
            self._reading_time(text, speed),
            "",
            "=== Word Statistics ===",
            self._word_stats(text),
            "",
            "=== Reading Level ===",
            self._reading_level(text),
        ]
        return "\n".join(parts)
