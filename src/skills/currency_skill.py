"""Currency converter skill – convert between currencies using fixed reference rates.

Covers the "Finance & Economics" category.
Pure Python, no external libraries.  Uses approximate rates relative to USD.

Supported actions
-----------------
convert         Convert an amount from one currency to another.
list_currencies List all supported currency codes.
rate            Show the exchange rate between two currencies.
compare         Compare how much 1 unit of source buys in multiple target currencies.
"""

from __future__ import annotations

# Approximate rates relative to USD (1 USD = X units)
# These are illustrative fixed rates – not live data.
_RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.50,
    "CAD": 1.36,
    "AUD": 1.53,
    "CHF": 0.90,
    "CNY": 7.24,
    "INR": 83.10,
    "MXN": 17.15,
    "BRL": 4.97,
    "KRW": 1330.0,
    "SGD": 1.34,
    "HKD": 7.82,
    "SEK": 10.42,
    "NOK": 10.56,
    "DKK": 6.88,
    "NZD": 1.63,
    "ZAR": 18.63,
    "RUB": 91.50,
    "TRY": 30.50,
    "PLN": 3.97,
    "THB": 35.10,
    "IDR": 15650.0,
    "HUF": 356.0,
    "CZK": 22.80,
    "ILS": 3.66,
    "CLP": 897.0,
    "PHP": 56.50,
    "AED": 3.67,
    "SAR": 3.75,
    "RON": 4.57,
    "MYR": 4.67,
    "NGN": 1540.0,
    "EGP": 30.90,
    "PKR": 279.0,
    "BDT": 110.0,
    "VND": 24380.0,
    "UAH": 37.50,
    "ARS": 835.0,
    "PEN": 3.72,
    "COP": 3950.0,
    "QAR": 3.64,
    "KWD": 0.307,
    "BHD": 0.376,
    "OMR": 0.384,
    "MAD": 10.07,
    "DZD": 134.0,
    "TZS": 2520.0,
    "ETB": 56.90,
    "GHS": 12.30,
    "KES": 154.0,
    "BTC": 0.000016,   # approximate
    "ETH": 0.00033,    # approximate
}


class CurrencySkill:
    """Convert between currencies using fixed reference rates (not live data)."""

    name = "currency"
    description = (
        "Currency conversion (approximate fixed rates, not live data). "
        "Supported actions: 'convert' (amount, from_currency, to_currency); "
        "'list_currencies'; 'rate' (from_currency, to_currency); "
        "'compare' (amount, from_currency, to_currencies – comma-separated)."
    )

    def run(
        self,
        action: str,
        amount: float = 1.0,
        from_currency: str = "USD",
        to_currency: str = "EUR",
        to_currencies: str = "",
    ) -> str:
        """
        Perform a currency conversion.

        Parameters
        ----------
        action:
            One of ``"convert"``, ``"list_currencies"``,
            ``"rate"``, ``"compare"``.
        amount:
            Amount to convert (default 1.0).
        from_currency:
            Source currency code (default ``"USD"``).
        to_currency:
            Target currency code.
        to_currencies:
            Comma-separated list of target codes for ``"compare"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "convert":
            return self._convert(amount, from_currency, to_currency)
        if action == "list_currencies":
            return "Supported currencies: " + ", ".join(sorted(_RATES))
        if action == "rate":
            return self._rate(from_currency, to_currency)
        if action == "compare":
            return self._compare(amount, from_currency, to_currencies or to_currency)
        return (
            f"Error: unknown action {action!r}. "
            "Use convert, list_currencies, rate, or compare."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _get_rate(code: str) -> float:
        code = code.strip().upper()
        if code not in _RATES:
            raise ValueError(f"Unknown currency code: {code!r}")
        return _RATES[code]

    def _convert(self, amount: float, src: str, dst: str) -> str:
        src = src.strip().upper()
        dst = dst.strip().upper()
        try:
            src_rate = self._get_rate(src)
            dst_rate = self._get_rate(dst)
        except ValueError as exc:
            return f"Error: {exc}"
        usd = amount / src_rate
        result = usd * dst_rate
        rate = dst_rate / src_rate
        return (
            f"{amount:,.4f} {src} = {result:,.4f} {dst}\n"
            f"(1 {src} = {rate:.6f} {dst}  |  approximate fixed rate)"
        )

    def _rate(self, src: str, dst: str) -> str:
        src = src.strip().upper()
        dst = dst.strip().upper()
        try:
            src_rate = self._get_rate(src)
            dst_rate = self._get_rate(dst)
        except ValueError as exc:
            return f"Error: {exc}"
        rate = dst_rate / src_rate
        return f"1 {src} = {rate:.6f} {dst}  (approximate fixed rate)"

    def _compare(self, amount: float, src: str, targets: str) -> str:
        src = src.strip().upper()
        try:
            src_rate = self._get_rate(src)
        except ValueError as exc:
            return f"Error: {exc}"
        codes = [t.strip().upper() for t in targets.split(",") if t.strip()]
        if not codes:
            return "Error: to_currencies is required for compare"
        lines = [f"{amount} {src} in other currencies (approx):"]
        for code in codes:
            try:
                dst_rate = self._get_rate(code)
            except ValueError:
                lines.append(f"  {code}: unknown currency")
                continue
            result = (amount / src_rate) * dst_rate
            lines.append(f"  {code:<6}: {result:>14,.4f}")
        return "\n".join(lines)
