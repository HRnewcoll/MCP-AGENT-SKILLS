"""Text processor skill – manipulate and analyse text strings."""

from __future__ import annotations

import re


class TextProcessorSkill:
    """Manipulate and analyse plain text strings."""

    name = "text_processor"
    description = (
        "Manipulate and analyse text. "
        "Supported actions: 'uppercase', 'lowercase', 'title_case', "
        "'word_count', 'char_count', 'line_count', 'replace', 'find', "
        "'reverse', 'trim', 'truncate', 'split', 'join', "
        "'snake_case', 'camel_case', 'repeat'."
    )

    def run(
        self,
        action: str,
        text: str = "",
        find: str = "",
        replace_with: str = "",
        max_length: int = 100,
        separator: str = "\n",
        count: int = 2,
    ) -> str:
        """
        Perform a text operation.

        Parameters
        ----------
        action:
            The operation to perform (see description for full list).
        text:
            The input text.
        find:
            Substring to find (for 'replace' and 'find').
        replace_with:
            Replacement string (for 'replace').
        max_length:
            Maximum character count for 'truncate' (default 100).
        separator:
            Separator string for 'split' and 'join' (default newline).
        count:
            Repeat count for 'repeat' (default 2).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "uppercase":
            return text.upper()
        if action == "lowercase":
            return text.lower()
        if action == "title_case":
            return text.title()
        if action == "word_count":
            return str(len(text.split()))
        if action == "char_count":
            return str(len(text))
        if action == "line_count":
            return str(len(text.splitlines()) if text else 0)
        if action == "reverse":
            return text[::-1]
        if action == "trim":
            return text.strip()
        if action == "truncate":
            return text if len(text) <= max_length else text[:max_length] + "..."
        if action == "replace":
            if not find:
                return "Error: find is required for replace"
            return text.replace(find, replace_with)
        if action == "find":
            if not find:
                return "Error: find is required for find"
            idx = text.find(find)
            return f"Found at index {idx}" if idx != -1 else f"Not found: {find!r}"
        if action == "split":
            parts = text.split(separator) if separator else text.split()
            return "\n".join(f"[{i}] {p}" for i, p in enumerate(parts))
        if action == "join":
            return separator.join(text.splitlines())
        if action == "snake_case":
            s = re.sub(r"([A-Z])", lambda m: " " + m.group(1).lower(), text.strip())
            s = re.sub(r"[\s\-]+", "_", s)
            return s.strip("_").lower()
        if action == "camel_case":
            parts = re.split(r"[\s_\-]+", text.strip())
            if not parts:
                return text
            return parts[0].lower() + "".join(p.title() for p in parts[1:])
        if action == "repeat":
            if count < 1:
                return "Error: count must be >= 1"
            return text * count
        return (
            f"Error: unknown action {action!r}. "
            "Use uppercase, lowercase, title_case, word_count, char_count, line_count, "
            "replace, find, reverse, trim, truncate, split, join, "
            "snake_case, camel_case, or repeat."
        )
