"""Permutation/combination skill – compute permutations, combinations, and related counts.

Covers the "Math & Education" category.
Uses Python stdlib ``math`` only.

Supported actions
-----------------
permutations    nPr = n! / (n-r)!
combinations    nCr = n! / (r! * (n-r)!)
factorial       n!
multinomial     Multinomial coefficient n! / (k1! * k2! * ...)
derangements    Number of derangements of n elements.
catalan         Nth Catalan number.
power_set_count Number of subsets of a set of size n (2^n).
list_permutations  List all permutations of a short string/list.
list_combinations  List all combinations of size r from items.
"""

from __future__ import annotations

import math
import itertools


class PermutationSkill:
    """Compute permutations, combinations, and related counting problems."""

    name = "permutation"
    description = (
        "Combinatorics and counting. "
        "Supported actions: 'permutations' (n, r); 'combinations' (n, r); "
        "'factorial' (n); 'multinomial' (values – comma-separated k values); "
        "'derangements' (n); 'catalan' (n); 'power_set_count' (n); "
        "'list_permutations' (items – comma-separated, max 8 items); "
        "'list_combinations' (items – comma-separated, r)."
    )

    def run(
        self,
        action: str,
        n: int = 0,
        r: int = 0,
        values: str = "",
        items: str = "",
    ) -> str:
        """
        Perform a combinatorics calculation.

        Parameters
        ----------
        action:
            The calculation to perform (see description).
        n:
            Total number of elements.
        r:
            Selection size (for permutations/combinations).
        values:
            Comma-separated group sizes for ``"multinomial"``.
        items:
            Comma-separated elements for listing (max 8).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "permutations":
                return self._perm(n, r)
            if action == "combinations":
                return self._comb(n, r)
            if action == "factorial":
                return self._fact(n)
            if action == "multinomial":
                return self._multi(values)
            if action == "derangements":
                return self._derange(n)
            if action == "catalan":
                return self._catalan(n)
            if action == "power_set_count":
                if n < 0:
                    return "Error: n must be >= 0"
                return str(2 ** n)
            if action == "list_permutations":
                return self._list_perms(items)
            if action == "list_combinations":
                return self._list_combs(items, r)
        except (ValueError, OverflowError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use permutations, combinations, factorial, multinomial, "
            "derangements, catalan, power_set_count, "
            "list_permutations, or list_combinations."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _perm(n: int, r: int) -> str:
        if n < 0 or r < 0:
            return "Error: n and r must be >= 0"
        if r > n:
            return "Error: r must be <= n"
        result = math.perm(n, r)
        return f"P({n},{r}) = {result:,}"

    @staticmethod
    def _comb(n: int, r: int) -> str:
        if n < 0 or r < 0:
            return "Error: n and r must be >= 0"
        if r > n:
            return "Error: r must be <= n"
        result = math.comb(n, r)
        return f"C({n},{r}) = {result:,}"

    @staticmethod
    def _fact(n: int) -> str:
        if n < 0:
            return "Error: n must be >= 0"
        if n > 1000:
            return "Error: n must be <= 1000"
        result = math.factorial(n)
        s = str(result)
        if len(s) > 60:
            return f"{n}! = {s[:20]}…{s[-10:]}  ({len(s)} digits)"
        return f"{n}! = {result:,}"

    @staticmethod
    def _multi(values: str) -> str:
        if not values:
            return "Error: values is required"
        ks = [int(x.strip()) for x in values.split(",") if x.strip()]
        if any(k < 0 for k in ks):
            return "Error: all values must be >= 0"
        n = sum(ks)
        num = math.factorial(n)
        den = 1
        for k in ks:
            den *= math.factorial(k)
        result = num // den
        return f"Multinomial({'+'.join(str(k) for k in ks)}) = {result:,}"

    @staticmethod
    def _derange(n: int) -> str:
        if n < 0:
            return "Error: n must be >= 0"
        # D(n) = (n-1)*(D(n-1)+D(n-2))
        if n == 0:
            return "D(0) = 1"
        if n == 1:
            return "D(1) = 0"
        prev2, prev1 = 1, 0
        for k in range(2, n + 1):
            curr = (k - 1) * (prev1 + prev2)
            prev2, prev1 = prev1, curr
        return f"D({n}) = {prev1:,}"

    @staticmethod
    def _catalan(n: int) -> str:
        if n < 0:
            return "Error: n must be >= 0"
        result = math.comb(2 * n, n) // (n + 1)
        return f"Catalan({n}) = {result:,}"

    @staticmethod
    def _list_perms(items: str) -> str:
        if not items:
            return "Error: items is required"
        elems = [x.strip() for x in items.split(",") if x.strip()]
        if len(elems) > 8:
            return "Error: list_permutations is limited to 8 items"
        perms = list(itertools.permutations(elems))
        result_lines = [f"{len(perms)} permutation(s) of {elems}:"]
        for p in perms[:50]:
            result_lines.append("  " + ", ".join(p))
        if len(perms) > 50:
            result_lines.append(f"  … (showing first 50 of {len(perms)})")
        return "\n".join(result_lines)

    @staticmethod
    def _list_combs(items: str, r: int) -> str:
        if not items:
            return "Error: items is required"
        if r <= 0:
            return "Error: r must be > 0"
        elems = [x.strip() for x in items.split(",") if x.strip()]
        if r > len(elems):
            return "Error: r must be <= number of items"
        combs = list(itertools.combinations(elems, r))
        result_lines = [f"{len(combs)} combination(s) of size {r} from {elems}:"]
        for c in combs[:50]:
            result_lines.append("  " + ", ".join(c))
        if len(combs) > 50:
            result_lines.append(f"  … (showing first 50 of {len(combs)})")
        return "\n".join(result_lines)
