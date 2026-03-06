"""Math sequence skill – generate and analyse mathematical sequences.

Covers the "Personal Development" and "Coding Agents & IDEs" categories.
Uses Python stdlib only.

Supported actions
-----------------
fibonacci       Generate the first N Fibonacci numbers.
primes          Generate all prime numbers up to N (Sieve of Eratosthenes).
is_prime        Check if a number is prime.
factorial       Compute N! (factorial).
triangular      Generate the first N triangular numbers.
perfect         Find perfect numbers up to N.
collatz         Generate the Collatz sequence for a starting number.
gcd             Compute the GCD of two numbers.
lcm             Compute the LCM of two numbers.
divisors        List all divisors of N.
"""

from __future__ import annotations

import math


class MathSequenceSkill:
    """Generate and analyse mathematical sequences and number properties."""

    name = "math_sequence"
    description = (
        "Mathematical sequences and number theory. "
        "Supported actions: 'fibonacci' (n); 'primes' (n=limit); "
        "'is_prime' (n); 'factorial' (n); 'triangular' (n); "
        "'perfect' (n=limit); 'collatz' (n); "
        "'gcd' (a, b); 'lcm' (a, b); 'divisors' (n)."
    )

    def run(
        self,
        action: str,
        n: int = 10,
        a: int = 0,
        b: int = 0,
    ) -> str:
        """
        Perform a math sequence operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        n:
            Primary numeric input (e.g. count, limit, or starting value).
        a, b:
            Two numbers for ``"gcd"`` and ``"lcm"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "fibonacci":
                return self._fibonacci(int(n))
            if action == "primes":
                return self._primes(int(n))
            if action == "is_prime":
                return self._is_prime(int(n))
            if action == "factorial":
                return self._factorial(int(n))
            if action == "triangular":
                return self._triangular(int(n))
            if action == "perfect":
                return self._perfect(int(n))
            if action == "collatz":
                return self._collatz(int(n))
            if action == "gcd":
                return self._gcd(int(a or n), int(b))
            if action == "lcm":
                return self._lcm(int(a or n), int(b))
            if action == "divisors":
                return self._divisors(int(n))
        except (ValueError, OverflowError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use fibonacci, primes, is_prime, factorial, triangular, "
            "perfect, collatz, gcd, lcm, or divisors."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _fibonacci(n: int) -> str:
        if n < 1:
            return "Error: n must be >= 1"
        if n > 100:
            return "Error: n must be <= 100"
        seq: list[int] = [0, 1]
        while len(seq) < n:
            seq.append(seq[-1] + seq[-2])
        return ", ".join(str(x) for x in seq[:n])

    @staticmethod
    def _primes(n: int) -> str:
        if n < 2:
            return "(no primes)"
        if n > 100_000:
            return "Error: limit must be <= 100,000"
        sieve = bytearray([1]) * (n + 1)
        sieve[0] = sieve[1] = 0
        for i in range(2, int(n**0.5) + 1):
            if sieve[i]:
                sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
        primes = [i for i, v in enumerate(sieve) if v]
        return f"{len(primes)} prime(s) up to {n}: " + ", ".join(str(p) for p in primes[:50]) + (
            f"  … (showing first 50)" if len(primes) > 50 else ""
        )

    @staticmethod
    def _is_prime(n: int) -> str:
        if n < 2:
            return f"{n} is NOT prime"
        if n == 2:
            return f"{n} IS prime"
        if n % 2 == 0:
            return f"{n} is NOT prime"
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return f"{n} is NOT prime (divisible by {i})"
        return f"{n} IS prime"

    @staticmethod
    def _factorial(n: int) -> str:
        if n < 0:
            return "Error: factorial of negative number is undefined"
        if n > 1000:
            return "Error: n must be <= 1000"
        result = math.factorial(n)
        result_str = str(result)
        if len(result_str) > 200:
            return f"{n}! has {len(result_str)} digits (too large to display)"
        return f"{n}! = {result}"

    @staticmethod
    def _triangular(n: int) -> str:
        if n < 1:
            return "Error: n must be >= 1"
        if n > 100:
            return "Error: n must be <= 100"
        seq = [i * (i + 1) // 2 for i in range(1, n + 1)]
        return ", ".join(str(x) for x in seq)

    @staticmethod
    def _perfect(n: int) -> str:
        if n < 1:
            return "(none)"
        if n > 10_000_000:
            return "Error: limit must be <= 10,000,000"
        perfects = []
        for num in range(2, n + 1):
            if sum(i for i in range(1, num) if num % i == 0) == num:
                perfects.append(num)
        if not perfects:
            return f"No perfect numbers up to {n}"
        return f"Perfect numbers up to {n}: " + ", ".join(str(p) for p in perfects)

    @staticmethod
    def _collatz(n: int) -> str:
        if n < 1:
            return "Error: n must be >= 1"
        if n > 10_000_000:
            return "Error: n must be <= 10,000,000"
        seq = [n]
        while n != 1 and len(seq) < 10000:
            n = n // 2 if n % 2 == 0 else 3 * n + 1
            seq.append(n)
        return f"Collatz({seq[0]}): {len(seq)} steps – " + ", ".join(str(x) for x in seq[:30]) + (
            " …" if len(seq) > 30 else ""
        )

    @staticmethod
    def _gcd(a: int, b: int) -> str:
        if not b:
            return "Error: both a and b are required for gcd"
        return f"GCD({a}, {b}) = {math.gcd(a, b)}"

    @staticmethod
    def _lcm(a: int, b: int) -> str:
        if not b:
            return "Error: both a and b are required for lcm"
        return f"LCM({a}, {b}) = {math.lcm(a, b)}"

    @staticmethod
    def _divisors(n: int) -> str:
        if n < 1:
            return "Error: n must be >= 1"
        if n > 10_000_000:
            return "Error: n must be <= 10,000,000"
        divs = sorted(i for i in range(1, n + 1) if n % i == 0)
        return f"Divisors of {n}: " + ", ".join(str(d) for d in divs)
