"""Tip calculator skill – calculate tips and split bills.

Covers the "Finance & Economics" and "Personal Development" categories.
Pure Python, no external libraries.

Supported actions
-----------------
calculate       Calculate tip amount and total for a bill.
split           Split a bill (with optional tip) among N people.
custom_splits   Split a bill with different percentages per person.
recommend       Suggest tip amounts at different percentages.
"""

from __future__ import annotations


class TipCalculatorSkill:
    """Calculate tips and split restaurant/group bills."""

    name = "tip_calculator"
    description = (
        "Calculate tips and split bills. "
        "Supported actions: 'calculate' (bill_amount, tip_percent); "
        "'split' (bill_amount, tip_percent, num_people); "
        "'custom_splits' (bill_amount, tip_percent, splits – comma-separated percentages); "
        "'recommend' (bill_amount)."
    )

    def run(
        self,
        action: str,
        bill_amount: float = 0.0,
        tip_percent: float = 15.0,
        num_people: int = 1,
        splits: str = "",
    ) -> str:
        """
        Perform a tip/bill calculation.

        Parameters
        ----------
        action:
            One of ``"calculate"``, ``"split"``,
            ``"custom_splits"``, ``"recommend"``.
        bill_amount:
            Pre-tip bill total.
        tip_percent:
            Tip percentage (default 15%).
        num_people:
            Number of people to split the bill between.
        splits:
            Comma-separated percentage shares for each person
            (must sum to 100).  E.g. ``"50, 25, 25"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if bill_amount <= 0:
            return "Error: bill_amount must be > 0"

        if action == "calculate":
            return self._calculate(bill_amount, tip_percent)
        if action == "split":
            return self._split(bill_amount, tip_percent, num_people)
        if action == "custom_splits":
            return self._custom_splits(bill_amount, tip_percent, splits)
        if action == "recommend":
            return self._recommend(bill_amount)
        return (
            f"Error: unknown action {action!r}. "
            "Use calculate, split, custom_splits, or recommend."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _calculate(bill: float, tip_pct: float) -> str:
        tip = bill * tip_pct / 100
        total = bill + tip
        return (
            f"Bill subtotal: ${bill:,.2f}\n"
            f"Tip ({tip_pct}%)  : ${tip:,.2f}\n"
            f"Total        : ${total:,.2f}"
        )

    @staticmethod
    def _split(bill: float, tip_pct: float, num_people: int) -> str:
        if num_people < 1:
            return "Error: num_people must be >= 1"
        tip = bill * tip_pct / 100
        total = bill + tip
        per_person = total / num_people
        return (
            f"Bill subtotal: ${bill:,.2f}\n"
            f"Tip ({tip_pct}%)  : ${tip:,.2f}\n"
            f"Total        : ${total:,.2f}\n"
            f"People       : {num_people}\n"
            f"Per person   : ${per_person:,.2f}"
        )

    @staticmethod
    def _custom_splits(bill: float, tip_pct: float, splits: str) -> str:
        if not splits:
            return "Error: splits is required"
        try:
            parts = [float(x.strip()) for x in splits.split(",") if x.strip()]
        except ValueError:
            return "Error: splits must be comma-separated numbers"
        if not parts:
            return "Error: at least one split percentage required"
        total_pct = sum(parts)
        if abs(total_pct - 100.0) > 0.01:
            return f"Error: split percentages must sum to 100 (got {total_pct:.2f})"
        tip = bill * tip_pct / 100
        total = bill + tip
        lines = [
            f"Bill: ${bill:,.2f}  Tip ({tip_pct}%): ${tip:,.2f}  Total: ${total:,.2f}"
        ]
        for i, pct in enumerate(parts, 1):
            share = total * pct / 100
            lines.append(f"  Person {i} ({pct:.1f}%): ${share:,.2f}")
        return "\n".join(lines)

    @staticmethod
    def _recommend(bill: float) -> str:
        lines = [f"Tip recommendations for ${bill:,.2f}:"]
        for pct in [10, 15, 18, 20, 25]:
            tip = bill * pct / 100
            total = bill + tip
            lines.append(f"  {pct:>2}%  tip: ${tip:,.2f}  total: ${total:,.2f}")
        return "\n".join(lines)
