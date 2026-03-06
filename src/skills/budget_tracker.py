"""Budget tracker skill – track income, expenses, and balances locally.

Covers the "Finance" category from the awesome-openclaw-skills directory.
All data is persisted to a local JSON file – no external APIs required.

Supported actions
-----------------
add_income      Record an income entry.
add_expense     Record an expense entry.
list            Show all transactions.
balance         Show current balance summary.
summary         Show totals grouped by category.
delete          Remove a transaction by ID.
clear           Remove all transactions.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class _Transaction(TypedDict):
    id: int
    type: str       # "income" | "expense"
    amount: float
    category: str
    description: str
    date: str


class BudgetTrackerSkill:
    """Track income and expenses locally – no external APIs needed."""

    name = "budget_tracker"
    description = (
        "Track personal budget – income and expenses. "
        "Supported actions: 'add_income' (amount, category, description); "
        "'add_expense' (amount, category, description); "
        "'list'; 'balance'; 'summary'; 'delete' (transaction_id); 'clear'."
    )

    def __init__(self, store_path: str | os.PathLike = ".budget.json") -> None:
        self._path = Path(store_path)
        self._transactions: list[_Transaction] = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        amount: float = 0.0,
        category: str = "General",
        description: str = "",
        transaction_id: int = 0,
    ) -> str:
        """
        Perform a budget operation.

        Parameters
        ----------
        action:
            One of ``"add_income"``, ``"add_expense"``, ``"list"``,
            ``"balance"``, ``"summary"``, ``"delete"``, ``"clear"``.
        amount:
            Monetary amount (required for add_income / add_expense).
        category:
            Category label (default ``"General"``).
        description:
            Optional free-text description.
        transaction_id:
            ID of the transaction to delete (required for ``"delete"``).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "add_income":
            return self._add("income", amount, category, description)
        if action == "add_expense":
            return self._add("expense", amount, category, description)
        if action == "list":
            return self._list()
        if action == "balance":
            return self._balance()
        if action == "summary":
            return self._summary()
        if action == "delete":
            return self._delete(transaction_id)
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use add_income, add_expense, list, balance, summary, delete, or clear."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add(self, tx_type: str, amount: float, category: str, description: str) -> str:
        if amount <= 0:
            return "Error: amount must be greater than 0"
        tx: _Transaction = {
            "id": self._next_id(),
            "type": tx_type,
            "amount": round(float(amount), 2),
            "category": category or "General",
            "description": description,
            "date": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._transactions.append(tx)
        self._save()
        sign = "+" if tx_type == "income" else "-"
        return f"#{tx['id']} {sign}${tx['amount']:.2f} [{tx['category']}] {description}"

    def _list(self) -> str:
        if not self._transactions:
            return "(no transactions)"
        lines = ["ID   Type     Amount     Category        Description"]
        lines.append("-" * 60)
        for t in self._transactions:
            sign = "+" if t["type"] == "income" else "-"
            lines.append(
                f"#{t['id']:<3} {t['type']:<8} {sign}${t['amount']:>8.2f} "
                f"{t['category']:<15} {t['description']}"
            )
        return "\n".join(lines)

    def _balance(self) -> str:
        income = sum(t["amount"] for t in self._transactions if t["type"] == "income")
        expense = sum(t["amount"] for t in self._transactions if t["type"] == "expense")
        balance = income - expense
        return (
            f"Income : +${income:.2f}\n"
            f"Expense: -${expense:.2f}\n"
            f"Balance:  ${balance:.2f}"
        )

    def _summary(self) -> str:
        if not self._transactions:
            return "(no transactions)"
        cats: dict[str, dict[str, float]] = {}
        for t in self._transactions:
            cat = t["category"]
            if cat not in cats:
                cats[cat] = {"income": 0.0, "expense": 0.0}
            cats[cat][t["type"]] += t["amount"]
        lines = ["Category        Income       Expense      Net"]
        lines.append("-" * 55)
        for cat, totals in sorted(cats.items()):
            net = totals["income"] - totals["expense"]
            lines.append(
                f"{cat:<16} +${totals['income']:>8.2f}   -${totals['expense']:>8.2f}   "
                f"${net:>+9.2f}"
            )
        return "\n".join(lines)

    def _delete(self, tx_id: int) -> str:
        if not tx_id:
            return "Error: transaction_id is required"
        tx = next((t for t in self._transactions if t["id"] == tx_id), None)
        if tx is None:
            return f"Error: transaction #{tx_id} not found"
        self._transactions.remove(tx)
        self._save()
        return f"Deleted transaction #{tx_id}"

    def _clear(self) -> str:
        count = len(self._transactions)
        self._transactions.clear()
        self._save()
        return f"Cleared {count} transaction(s)"

    def _next_id(self) -> int:
        return max((t["id"] for t in self._transactions), default=0) + 1

    def _load(self) -> list[_Transaction]:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._transactions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
