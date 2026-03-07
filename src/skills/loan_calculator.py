"""Loan calculator skill – mortgage, loan, and interest calculations.

Covers the "Finance & Economics" category.
Uses Python stdlib ``math`` only.

Supported actions
-----------------
monthly_payment     Monthly mortgage/loan payment (principal, annual_rate, years).
total_interest      Total interest paid over the loan term.
amortize            Print a short amortization schedule.
compound_periods    How many periods to reach a target with compound interest.
simple_interest     Simple interest calculation.
apr_to_monthly      Convert APR to monthly rate.
"""

from __future__ import annotations

import math


class LoanCalculatorSkill:
    """Perform mortgage, loan, and interest calculations."""

    name = "loan_calculator"
    description = (
        "Loan and mortgage calculations. "
        "Supported actions: 'monthly_payment' (principal, annual_rate, years); "
        "'total_interest' (principal, annual_rate, years); "
        "'amortize' (principal, annual_rate, years, periods=12); "
        "'compound_periods' (principal, rate_per_period, target); "
        "'simple_interest' (principal, annual_rate, years); "
        "'apr_to_monthly' (annual_rate)."
    )

    def run(
        self,
        action: str,
        principal: float = 0.0,
        annual_rate: float = 0.0,
        years: float = 0.0,
        target: float = 0.0,
        rate_per_period: float = 0.0,
        periods: int = 12,
    ) -> str:
        """
        Perform a loan/interest calculation.

        Parameters
        ----------
        action:
            The calculation to perform (see description).
        principal:
            Loan or investment principal amount.
        annual_rate:
            Annual interest rate as a percentage (e.g. ``5.5`` for 5.5%).
        years:
            Loan term in years.
        target:
            Target balance for ``"compound_periods"``.
        rate_per_period:
            Interest rate per period as a decimal for ``"compound_periods"``.
        periods:
            Periods to show in ``"amortize"`` (default 12).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "monthly_payment":
                return self._monthly_payment(principal, annual_rate, years)
            if action == "total_interest":
                return self._total_interest(principal, annual_rate, years)
            if action == "amortize":
                return self._amortize(principal, annual_rate, years, periods)
            if action == "compound_periods":
                return self._compound_periods(principal, rate_per_period, target)
            if action == "simple_interest":
                return self._simple_interest(principal, annual_rate, years)
            if action == "apr_to_monthly":
                return self._apr_to_monthly(annual_rate)
        except (ValueError, ZeroDivisionError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use monthly_payment, total_interest, amortize, "
            "compound_periods, simple_interest, or apr_to_monthly."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _monthly_payment(principal: float, annual_rate: float, years: float) -> str:
        if principal <= 0:
            return "Error: principal must be > 0"
        if years <= 0:
            return "Error: years must be > 0"
        if annual_rate == 0:
            payment = principal / (years * 12)
            return f"Monthly payment: ${payment:,.2f} (0% interest)"
        r = annual_rate / 100 / 12
        n = years * 12
        payment = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
        return (
            f"Principal     : ${principal:,.2f}\n"
            f"Annual rate   : {annual_rate}%\n"
            f"Term          : {years} year(s)\n"
            f"Monthly payment: ${payment:,.2f}"
        )

    @staticmethod
    def _total_interest(principal: float, annual_rate: float, years: float) -> str:
        if principal <= 0 or years <= 0:
            return "Error: principal and years must be > 0"
        if annual_rate == 0:
            return f"Total interest: $0.00"
        r = annual_rate / 100 / 12
        n = years * 12
        payment = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
        total_paid = payment * n
        total_interest = total_paid - principal
        return (
            f"Total paid    : ${total_paid:,.2f}\n"
            f"Principal     : ${principal:,.2f}\n"
            f"Total interest: ${total_interest:,.2f}"
        )

    @staticmethod
    def _amortize(principal: float, annual_rate: float, years: float, periods: int) -> str:
        if principal <= 0 or years <= 0:
            return "Error: principal and years must be > 0"
        r = annual_rate / 100 / 12 if annual_rate > 0 else 0
        n = int(years * 12)
        periods = max(1, min(int(periods), n))
        if r == 0:
            payment = principal / n
        else:
            payment = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
        balance = principal
        lines = [f"{'Period':>6}  {'Payment':>12}  {'Principal':>12}  {'Interest':>12}  {'Balance':>14}"]
        lines.append("-" * 64)
        for i in range(1, periods + 1):
            interest = balance * r
            principal_paid = payment - interest
            balance -= principal_paid
            balance = max(0.0, balance)
            lines.append(
                f"{i:>6}  ${payment:>11,.2f}  ${principal_paid:>11,.2f}  "
                f"${interest:>11,.2f}  ${balance:>13,.2f}"
            )
        return "\n".join(lines)

    @staticmethod
    def _compound_periods(principal: float, rate_per_period: float, target: float) -> str:
        if principal <= 0 or target <= 0:
            return "Error: principal and target must be > 0"
        if rate_per_period <= 0:
            return "Error: rate_per_period must be > 0"
        if target <= principal:
            return "Error: target must be > principal"
        periods = math.log(target / principal) / math.log(1 + rate_per_period)
        return (
            f"Periods needed: {periods:.2f}\n"
            f"(principal=${principal:,.2f}  rate={rate_per_period*100:.4f}%/period  "
            f"target=${target:,.2f})"
        )

    @staticmethod
    def _simple_interest(principal: float, annual_rate: float, years: float) -> str:
        if principal <= 0 or years <= 0:
            return "Error: principal and years must be > 0"
        interest = principal * (annual_rate / 100) * years
        return (
            f"Principal    : ${principal:,.2f}\n"
            f"Rate         : {annual_rate}% per year\n"
            f"Term         : {years} year(s)\n"
            f"Interest     : ${interest:,.2f}\n"
            f"Total        : ${principal + interest:,.2f}"
        )

    @staticmethod
    def _apr_to_monthly(annual_rate: float) -> str:
        monthly = annual_rate / 100 / 12
        effective = (1 + monthly) ** 12 - 1
        return (
            f"APR          : {annual_rate}%\n"
            f"Monthly rate : {monthly * 100:.6f}%\n"
            f"Effective APY: {effective * 100:.4f}%"
        )
