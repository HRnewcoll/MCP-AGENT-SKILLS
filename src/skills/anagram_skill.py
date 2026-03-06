"""Anagram skill – check for anagrams, find anagrams in word lists, and scramble words.

Covers the "Personal Development" and "Gaming" categories.
Uses Python stdlib only.

Supported actions
-----------------
is_anagram      Check if two strings are anagrams of each other.
find            Find all anagrams of a word in a provided word list.
scramble        Randomly scramble the letters of a word.
sort_letters    Sort letters of a word alphabetically (canonical form).
anagram_key     Return the canonical sorted-letter key for grouping.
"""

from __future__ import annotations

import secrets
import re


def _canonical(word: str) -> str:
    """Return sorted lowercase letters of word (used as anagram key)."""
    return "".join(sorted(re.sub(r"[^a-zA-Z]", "", word.lower())))


class AnagramSkill:
    """Check for anagrams, scramble words, and find anagram groups."""

    name = "anagram"
    description = (
        "Anagram utilities. "
        "Supported actions: 'is_anagram' (word1, word2); "
        "'find' (word, word_list – comma-separated); "
        "'scramble' (word); 'sort_letters' (word); "
        "'anagram_key' (word)."
    )

    def run(
        self,
        action: str,
        word: str = "",
        word1: str = "",
        word2: str = "",
        word_list: str = "",
    ) -> str:
        """
        Perform an anagram operation.

        Parameters
        ----------
        action:
            One of ``"is_anagram"``, ``"find"``, ``"scramble"``,
            ``"sort_letters"``, ``"anagram_key"``.
        word:
            The word to operate on for scramble/sort_letters/find/anagram_key.
        word1 / word2:
            Two words for ``"is_anagram"``.
        word_list:
            Comma-separated list of words to search in for ``"find"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "is_anagram":
            return self._is_anagram(word1 or word, word2)
        if action == "find":
            return self._find(word, word_list)
        if action == "scramble":
            return self._scramble(word)
        if action == "sort_letters":
            if not word:
                return "Error: word is required"
            return _canonical(word)
        if action == "anagram_key":
            if not word:
                return "Error: word is required"
            return _canonical(word)
        return (
            f"Error: unknown action {action!r}. "
            "Use is_anagram, find, scramble, sort_letters, or anagram_key."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _is_anagram(w1: str, w2: str) -> str:
        if not w1 or not w2:
            return "Error: word1 and word2 are required for is_anagram"
        key1 = _canonical(w1)
        key2 = _canonical(w2)
        if not key1 or not key2:
            return "Error: words must contain at least one letter"
        result = "ARE anagrams" if key1 == key2 else "are NOT anagrams"
        return f"'{w1}' and '{w2}' {result}"

    @staticmethod
    def _find(word: str, word_list: str) -> str:
        if not word:
            return "Error: word is required for find"
        if not word_list:
            return "Error: word_list is required for find"
        key = _canonical(word)
        candidates = [w.strip() for w in word_list.split(",") if w.strip()]
        matches = [
            w for w in candidates
            if _canonical(w) == key and w.lower() != word.lower()
        ]
        if not matches:
            return f"No anagrams of '{word}' found in the word list"
        return f"Anagrams of '{word}': " + ", ".join(matches)

    @staticmethod
    def _scramble(word: str) -> str:
        if not word:
            return "Error: word is required for scramble"
        letters = list(word)
        for i in range(len(letters) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            letters[i], letters[j] = letters[j], letters[i]
        return "".join(letters)
