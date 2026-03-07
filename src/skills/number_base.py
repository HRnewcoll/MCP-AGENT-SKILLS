"""Number base converter skill – convert numbers between numeric bases.

Covers the "CLI Utilities" and "Coding Agents & IDEs" categories from the
awesome-openclaw-skills directory.  Uses Python stdlib only.

Supported actions
-----------------
to_binary   Convert a decimal integer to binary (base 2).
to_octal    Convert a decimal integer to octal (base 8).
to_hex      Convert a decimal integer to hexadecimal (base 16).
to_decimal  Convert a number in a given base to decimal.
convert     Convert a number from any base (2-36) to any other base.
table       Show a conversion table for a number across common bases.
"""

from __future__ import annotations

import re


_BASE_NAMES = {2: "binary", 8: "octal", 10: "decimal", 16: "hexadecimal"}


def _to_base(n: int, base: int) -> str:
    """Convert non-negative integer *n* to string in *base*."""
    if n == 0:
        return "0"
    digits = []
    negative = n < 0
    n = abs(n)
    while n:
        digits.append("0123456789abcdefghijklmnopqrstuvwxyz"[n % base])
        n //= base
    if negative:
        digits.append("-")
    return "".join(reversed(digits))


class NumberBaseSkill:
    """Convert numbers between different numeric bases (2-36)."""

    name = "number_base"
    description = (
        "Convert numbers between numeric bases. "
        "Supported actions: 'to_binary' (number); 'to_octal' (number); "
        "'to_hex' (number); 'to_decimal' (number, from_base); "
        "'convert' (number, from_base, to_base); 'table' (number, from_base)."
    )

    def run(
        self,
        action: str,
        number: str = "0",
        from_base: int = 10,
        to_base: int = 10,
    ) -> str:
        """
        Perform a base conversion.

        Parameters
        ----------
        action:
            One of ``"to_binary"``, ``"to_octal"``, ``"to_hex"``,
            ``"to_decimal"``, ``"convert"``, ``"table"``.
        number:
            The number to convert (as a string, to support any base).
        from_base:
            Source base (default 10).
        to_base:
            Target base for ``"convert"`` (default 10).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "to_binary":
            return self._convert_inner(number, from_base, 2)
        if action == "to_octal":
            return self._convert_inner(number, from_base, 8)
        if action == "to_hex":
            return self._convert_inner(number, from_base, 16)
        if action == "to_decimal":
            return self._convert_inner(number, from_base, 10)
        if action == "convert":
            return self._convert_inner(number, from_base, to_base)
        if action == "table":
            return self._table(number, from_base)
        return (
            f"Error: unknown action {action!r}. "
            "Use to_binary, to_octal, to_hex, to_decimal, convert, or table."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse(number: str, from_base: int) -> "int | str":
        try:
            return int(str(number).strip(), int(from_base))
        except (ValueError, TypeError):
            return f"Error: {number!r} is not a valid base-{from_base} number"

    @staticmethod
    def _validate_base(base: int) -> "str | None":
        b = int(base)
        if b < 2 or b > 36:
            return f"Error: base must be between 2 and 36 (got {b})"
        return None

    def _convert_inner(self, number: str, from_base: int, to_base: int) -> str:
        err = self._validate_base(from_base)
        if err:
            return err
        err = self._validate_base(to_base)
        if err:
            return err
        n = self._parse(number, from_base)
        if isinstance(n, str):
            return n
        result = _to_base(n, to_base)
        from_name = _BASE_NAMES.get(int(from_base), f"base-{from_base}")
        to_name = _BASE_NAMES.get(int(to_base), f"base-{to_base}")
        prefix = {2: "0b", 8: "0o", 16: "0x"}.get(int(to_base), "")
        return f"{number} ({from_name}) = {prefix}{result} ({to_name})"

    def _table(self, number: str, from_base: int) -> str:
        err = self._validate_base(from_base)
        if err:
            return err
        n = self._parse(number, from_base)
        if isinstance(n, str):
            return n
        rows = [
            ("Decimal (10)", str(n)),
            ("Binary (2)", f"0b{_to_base(n, 2)}"),
            ("Octal (8)", f"0o{_to_base(n, 8)}"),
            ("Hexadecimal (16)", f"0x{_to_base(n, 16)}"),
            ("Base 32", _to_base(n, 32)),
            ("Base 36", _to_base(n, 36)),
        ]
        lines = [f"Conversion table for {number} (base {from_base}):"]
        for label, val in rows:
            lines.append(f"  {label:<20} {val}")
        return "\n".join(lines)
