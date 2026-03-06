"""Palindrome skill – check, find, and generate palindromes.

Covers the "Personal Development" and "Gaming" categories.
Pure Python, no external libraries.

Supported actions
-----------------
is_palindrome   Check if a string is a palindrome.
find            Find all palindromic substrings of length >= min_len.
longest         Find the longest palindromic substring.
make            Try to extend a string into a palindrome.
reverse_words   Reverse words in a sentence to form a sentence palindrome.
is_number       Check if a number is a palindrome.
"""

from __future__ import annotations

import re


def _normalize(s: str) -> str:
    """Lowercase and remove non-alphanumeric characters."""
    return re.sub(r"[^a-zA-Z0-9]", "", s).lower()


def _is_palindrome(s: str) -> bool:
    n = _normalize(s)
    return n == n[::-1]


class PalindromeSkill:
    """Check, find, and work with palindromes."""

    name = "palindrome"
    description = (
        "Palindrome utilities. "
        "Supported actions: 'is_palindrome' (text); "
        "'find' (text, min_len=3); 'longest' (text); "
        "'make' (text); 'reverse_words' (text); "
        "'is_number' (n)."
    )

    def run(
        self,
        action: str,
        text: str = "",
        n: int = 0,
        min_len: int = 3,
    ) -> str:
        """
        Perform a palindrome operation.

        Parameters
        ----------
        action:
            One of ``"is_palindrome"``, ``"find"``, ``"longest"``,
            ``"make"``, ``"reverse_words"``, ``"is_number"``.
        text:
            Input string.
        n:
            Integer for ``"is_number"``.
        min_len:
            Minimum length of palindromic substrings to find
            (default 3).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "is_palindrome":
            return self._is_pal(text)
        if action == "find":
            return self._find(text, int(min_len))
        if action == "longest":
            return self._longest(text)
        if action == "make":
            return self._make(text)
        if action == "reverse_words":
            return self._reverse_words(text)
        if action == "is_number":
            return self._is_number(int(n) if n else 0, text)
        return (
            f"Error: unknown action {action!r}. "
            "Use is_palindrome, find, longest, make, reverse_words, or is_number."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _is_pal(text: str) -> str:
        if not text:
            return "Error: text is required"
        result = "IS" if _is_palindrome(text) else "is NOT"
        return f"'{text}' {result} a palindrome"

    @staticmethod
    def _find(text: str, min_len: int) -> str:
        if not text:
            return "Error: text is required"
        found: set[str] = set()
        s = text
        for i in range(len(s)):
            for j in range(i + min_len, len(s) + 1):
                sub = s[i:j]
                if _is_palindrome(sub) and len(sub) >= min_len:
                    found.add(sub)
        if not found:
            return f"No palindromic substrings of length >= {min_len} found"
        return f"{len(found)} palindromic substring(s):\n" + ", ".join(
            sorted(found, key=len, reverse=True)[:20]
        ) + (" …" if len(found) > 20 else "")

    @staticmethod
    def _longest(text: str) -> str:
        if not text:
            return "Error: text is required"
        best = ""
        s = text
        for i in range(len(s)):
            for j in range(i + 1, len(s) + 1):
                sub = s[i:j]
                if _is_palindrome(sub) and len(sub) > len(best):
                    best = sub
        if not best:
            return "No palindromic substring found"
        return f"Longest palindrome: '{best}' ({len(best)} chars)"

    @staticmethod
    def _make(text: str) -> str:
        """Return the shortest palindrome starting with *text* by appending reversed prefix."""
        if not text:
            return "Error: text is required"
        s = text
        # Find the longest palindromic suffix and append the remaining prefix reversed
        for i in range(len(s) + 1):
            if _is_palindrome(s[i:]):
                candidate = s + s[:i][::-1]
                return f"Palindrome from '{text}': '{candidate}'"
        return text  # fallback (shouldn't happen)

    @staticmethod
    def _reverse_words(text: str) -> str:
        if not text:
            return "Error: text is required"
        words = text.split()
        reversed_words = " ".join(reversed(words))
        return f"Original     : {text}\nReversed words: {reversed_words}"

    @staticmethod
    def _is_number(n: int, text: str) -> str:
        if n:
            num = n
        elif (text or "").strip().lstrip("-").isdigit():
            num = int(text.strip())
        else:
            return "Error: n (integer) is required for is_number"
        s = str(abs(num))
        result = "IS" if s == s[::-1] else "is NOT"
        return f"{num} {result} a palindrome number"
