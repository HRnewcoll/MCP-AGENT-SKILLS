"""Roman numeral skill – convert between Arabic and Roman numerals.

Covers the "CLI Utilities" and "Personal Development" categories.
Pure Python, no external libraries.

Supported actions
-----------------
to_roman        Convert an Arabic integer (1–3999) to Roman numeral.
to_arabic       Convert a Roman numeral string to an Arabic integer.
is_valid        Check if a string is a valid Roman numeral.
range_convert   Convert a range of integers to Roman numerals.
"""

from __future__ import annotations

_TO_ROMAN = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100,  "C"), (90,  "XC"), (50,  "L"), (40,  "XL"),
    (10,   "X"), (9,   "IX"), (5,   "V"), (4,   "IV"),
    (1,    "I"),
]

_ROMAN_VALUES: dict[str, int] = {
    "I": 1, "V": 5, "X": 10, "L": 50,
    "C": 100, "D": 500, "M": 1000,
}


def _int_to_roman(n: int) -> str:
    if not 1 <= n <= 3999:
        raise ValueError("Number must be between 1 and 3999")
    result = []
    for value, numeral in _TO_ROMAN:
        while n >= value:
            result.append(numeral)
            n -= value
    return "".join(result)


def _roman_to_int(s: str) -> int:
    s = s.strip().upper()
    if not s:
        raise ValueError("Empty Roman numeral")
    result = 0
    prev = 0
    for ch in reversed(s):
        if ch not in _ROMAN_VALUES:
            raise ValueError(f"Invalid Roman numeral character: {ch!r}")
        val = _ROMAN_VALUES[ch]
        if val < prev:
            result -= val
        else:
            result += val
        prev = val
    # Validate round-trip
    if _int_to_roman(result) != s:
        raise ValueError(f"{s!r} is not a standard Roman numeral")
    return result


class RomanNumeralSkill:
    """Convert between Arabic integers and Roman numerals."""

    name = "roman_numeral"
    description = (
        "Convert between Arabic integers and Roman numerals. "
        "Supported actions: 'to_roman' (n); 'to_arabic' (roman); "
        "'is_valid' (roman); 'range_convert' (start, end)."
    )

    def run(
        self,
        action: str,
        n: int = 0,
        roman: str = "",
        start: int = 1,
        end: int = 10,
    ) -> str:
        """
        Perform a Roman numeral conversion.

        Parameters
        ----------
        action:
            One of ``"to_roman"``, ``"to_arabic"``, ``"is_valid"``,
            ``"range_convert"``.
        n:
            Arabic integer for ``"to_roman"`` (1–3999).
        roman:
            Roman numeral string for ``"to_arabic"`` and ``"is_valid"``.
        start / end:
            Range for ``"range_convert"`` (inclusive; max range = 50).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "to_roman":
                if not n:
                    return "Error: n is required for to_roman"
                return _int_to_roman(int(n))

            if action == "to_arabic":
                if not roman:
                    return "Error: roman is required for to_arabic"
                return str(_roman_to_int(roman))

            if action == "is_valid":
                if not roman:
                    return "Error: roman is required for is_valid"
                try:
                    _roman_to_int(roman)
                    return f"'{roman.upper()}' is a valid Roman numeral"
                except ValueError:
                    return f"'{roman}' is NOT a valid Roman numeral"

            if action == "range_convert":
                start_i, end_i = int(start), int(end)
                if start_i < 1 or end_i > 3999:
                    return "Error: range must be within 1–3999"
                if end_i - start_i > 49:
                    return "Error: range is limited to 50 values at a time"
                return "\n".join(
                    f"{i} = {_int_to_roman(i)}" for i in range(start_i, end_i + 1)
                )

        except (ValueError, TypeError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use to_roman, to_arabic, is_valid, or range_convert."
        )
