"""Finance skill – compound interest, ROI, NPV, FV, PV, and savings calculations.

Covers the "Finance & Economics" category.
Uses Python stdlib ``math`` only.

Supported actions
-----------------
compound_interest   Compound interest (FV given PV, rate, n, compounds/year).
future_value        Future value of regular payments (annuity FV).
present_value       Present value of a future sum.
roi                 Return on Investment as a percentage.
npv                 Net Present Value of cash flows.
break_even          Break-even analysis (units to cover fixed cost).
savings_goal        How long to reach a savings goal.
inflation_adjust    Adjust a value for inflation.
"""

from __future__ import annotations

import math


class FinanceSkill:
    """Financial calculations: compound interest, ROI, NPV, and more."""

    name = "finance"
    description = (
        "Financial calculations. "
        "Supported actions: "
        "'compound_interest' (principal, annual_rate, years, compounds_per_year=12); "
        "'future_value' (payment, annual_rate, years, compounds_per_year=12); "
        "'present_value' (future_amount, annual_rate, years); "
        "'roi' (initial_investment, final_value); "
        "'npv' (rate, cash_flows – comma-separated, including initial negative investment); "
        "'break_even' (fixed_cost, price_per_unit, variable_cost_per_unit); "
        "'savings_goal' (goal, monthly_deposit, annual_rate); "
        "'inflation_adjust' (amount, annual_inflation, years)."
    )

    def run(
        self,
        action: str,
        principal: float = 0.0,
        annual_rate: float = 0.0,
        years: float = 0.0,
        compounds_per_year: int = 12,
        payment: float = 0.0,
        future_amount: float = 0.0,
        initial_investment: float = 0.0,
        final_value: float = 0.0,
        cash_flows: str = "",
        rate: float = 0.0,
        fixed_cost: float = 0.0,
        price_per_unit: float = 0.0,
        variable_cost_per_unit: float = 0.0,
        goal: float = 0.0,
        monthly_deposit: float = 0.0,
        annual_inflation: float = 0.0,
        amount: float = 0.0,
    ) -> str:
        action = action.strip().lower()

        try:
            if action == "compound_interest":
                return self._compound(principal, annual_rate, years, compounds_per_year)
            if action == "future_value":
                return self._fv(payment, annual_rate, years, compounds_per_year)
            if action == "present_value":
                return self._pv(future_amount, annual_rate, years)
            if action == "roi":
                return self._roi(initial_investment, final_value)
            if action == "npv":
                return self._npv(rate, cash_flows)
            if action == "break_even":
                return self._break_even(fixed_cost, price_per_unit, variable_cost_per_unit)
            if action == "savings_goal":
                return self._savings_goal(goal, monthly_deposit, annual_rate)
            if action == "inflation_adjust":
                return self._inflation(amount or principal, annual_inflation, years)
        except (ValueError, ZeroDivisionError) as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use compound_interest, future_value, present_value, roi, "
            "npv, break_even, savings_goal, or inflation_adjust."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _compound(p: float, r: float, t: float, n: int) -> str:
        if p <= 0 or t <= 0:
            return "Error: principal and years must be > 0"
        r_dec = r / 100
        fv = p * (1 + r_dec / n) ** (n * t)
        interest = fv - p
        return (
            f"Principal    : ${p:,.2f}\n"
            f"Rate         : {r}% / year\n"
            f"Compounds    : {n}×/year\n"
            f"Years        : {t}\n"
            f"Future value : ${fv:,.2f}\n"
            f"Interest     : ${interest:,.2f}"
        )

    @staticmethod
    def _fv(pmt: float, r: float, t: float, n: int) -> str:
        if pmt <= 0 or t <= 0:
            return "Error: payment and years must be > 0"
        r_per = r / 100 / n
        periods = n * t
        if r_per == 0:
            fv = pmt * periods
        else:
            fv = pmt * ((1 + r_per) ** periods - 1) / r_per
        return (
            f"Payment      : ${pmt:,.2f} / period\n"
            f"Rate         : {r}% / year ({n} compounds)\n"
            f"Years        : {t}\n"
            f"Future value : ${fv:,.2f}"
        )

    @staticmethod
    def _pv(fv: float, r: float, t: float) -> str:
        if fv <= 0 or t <= 0:
            return "Error: future_amount and years must be > 0"
        r_dec = r / 100
        if r_dec == 0:
            return f"Present value: ${fv:,.2f} (0% rate)"
        pv = fv / (1 + r_dec) ** t
        return (
            f"Future amount : ${fv:,.2f}\n"
            f"Discount rate : {r}% / year\n"
            f"Years         : {t}\n"
            f"Present value : ${pv:,.2f}"
        )

    @staticmethod
    def _roi(invested: float, final: float) -> str:
        if invested <= 0:
            return "Error: initial_investment must be > 0"
        gain = final - invested
        roi = (gain / invested) * 100
        return (
            f"Initial investment: ${invested:,.2f}\n"
            f"Final value       : ${final:,.2f}\n"
            f"Gain/Loss         : ${gain:,.2f}\n"
            f"ROI               : {roi:.2f}%"
        )

    @staticmethod
    def _npv(rate: float, cash_flows: str) -> str:
        if not cash_flows:
            return "Error: cash_flows is required"
        try:
            flows = [float(x.strip()) for x in cash_flows.split(",") if x.strip()]
        except ValueError:
            return "Error: cash_flows must be comma-separated numbers"
        r = rate / 100 if rate > 1 else rate
        npv = sum(cf / (1 + r) ** t for t, cf in enumerate(flows))
        return (
            f"Cash flows: {flows}\n"
            f"Rate      : {rate}%\n"
            f"NPV       : ${npv:,.2f}"
        )

    @staticmethod
    def _break_even(fixed: float, price: float, variable: float) -> str:
        if price <= 0:
            return "Error: price_per_unit must be > 0"
        if price <= variable:
            return "Error: price_per_unit must be > variable_cost_per_unit"
        units = math.ceil(fixed / (price - variable))
        revenue = units * price
        return (
            f"Fixed cost   : ${fixed:,.2f}\n"
            f"Price/unit   : ${price:,.2f}\n"
            f"Variable/unit: ${variable:,.2f}\n"
            f"Break-even   : {units} unit(s)\n"
            f"Revenue      : ${revenue:,.2f}"
        )

    @staticmethod
    def _savings_goal(goal: float, monthly: float, r: float) -> str:
        if goal <= 0 or monthly <= 0:
            return "Error: goal and monthly_deposit must be > 0"
        r_monthly = r / 100 / 12
        if r_monthly == 0:
            months = math.ceil(goal / monthly)
        else:
            months = math.ceil(
                math.log(1 + goal * r_monthly / monthly) / math.log(1 + r_monthly)
            )
        years = months // 12
        extra_months = months % 12
        return (
            f"Goal          : ${goal:,.2f}\n"
            f"Monthly deposit: ${monthly:,.2f}\n"
            f"Rate          : {r}%/year\n"
            f"Time to goal  : {months} months ({years}y {extra_months}m)"
        )

    @staticmethod
    def _inflation(amount: float, inflation: float, years: float) -> str:
        if amount <= 0 or years <= 0:
            return "Error: amount and years must be > 0"
        r = inflation / 100
        future_equiv = amount * (1 + r) ** years
        purchasing_power = amount / (1 + r) ** years
        return (
            f"Today's amount      : ${amount:,.2f}\n"
            f"Inflation           : {inflation}%/year\n"
            f"Years               : {years}\n"
            f"Equivalent cost then: ${future_equiv:,.2f}\n"
            f"Today's buying power: ${purchasing_power:,.2f}"
        )
