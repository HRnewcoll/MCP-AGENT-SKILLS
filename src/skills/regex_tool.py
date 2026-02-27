"""Regex tool skill – test and apply regular expressions."""

from __future__ import annotations

import re


class RegexToolSkill:
    """Test and apply regular expressions to text."""

    name = "regex_tool"
    description = (
        "Test and apply regular expressions. "
        "Supported actions: 'match' (anchor at start), 'search' (find anywhere), "
        "'findall' (all occurrences), 'replace' (substitute pattern), "
        "'split' (split text by pattern), 'validate' (full-string match)."
    )

    _MAX_RESULTS = 50

    def run(
        self,
        action: str,
        pattern: str,
        text: str = "",
        replacement: str = "",
        flags: str = "",
    ) -> str:
        """
        Apply *pattern* to *text*.

        Parameters
        ----------
        action:
            One of ``"match"``, ``"search"``, ``"findall"``, ``"replace"``,
            ``"split"``, ``"validate"``.
        pattern:
            Regular expression pattern string.
        text:
            Input text to process.
        replacement:
            Replacement string for 'replace' (supports ``\\1`` backreferences).
        flags:
            Optional modifier characters: ``"i"`` (ignore case),
            ``"m"`` (multiline), ``"s"`` (dot-all).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if not pattern:
            return "Error: pattern is required"

        compiled_flags = 0
        for f in flags.lower():
            if f == "i":
                compiled_flags |= re.IGNORECASE
            elif f == "m":
                compiled_flags |= re.MULTILINE
            elif f == "s":
                compiled_flags |= re.DOTALL

        try:
            compiled = re.compile(pattern, compiled_flags)
        except re.error as exc:
            return f"Error: invalid pattern – {exc}"

        if action == "match":
            m = compiled.match(text)
            if m is None:
                return "No match"
            groups = m.groups()
            extra = f"\nGroups: {groups}" if groups else ""
            return f"Matched: {m.group()!r}{extra}"

        if action == "search":
            m = compiled.search(text)
            if m is None:
                return "No match"
            groups = m.groups()
            extra = f"\nGroups: {groups}" if groups else ""
            return f"Found at {m.start()}: {m.group()!r}{extra}"

        if action == "findall":
            results = compiled.findall(text)
            if not results:
                return "No matches"
            limited = results[: self._MAX_RESULTS]
            suffix = (
                f"\n(showing {self._MAX_RESULTS} of {len(results)})"
                if len(results) > self._MAX_RESULTS
                else ""
            )
            return f"{len(results)} match(es):\n" + "\n".join(repr(r) for r in limited) + suffix

        if action == "replace":
            try:
                return compiled.sub(replacement, text)
            except re.error as exc:
                return f"Error: {exc}"

        if action == "split":
            parts = compiled.split(text)
            return "\n".join(f"[{i}] {p!r}" for i, p in enumerate(parts))

        if action == "validate":
            return "Valid (full match)" if compiled.fullmatch(text) else "Invalid (no full match)"

        return (
            f"Error: unknown action {action!r}. "
            "Use match, search, findall, replace, split, or validate."
        )
