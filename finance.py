"""Personal Finance Manager - CLI app demonstrating Python fundamentals + OOP."""
from __future__ import annotations
import json
import os
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date, datetime

DATA_FILE = "transactions.json"
CATEGORIES = ["Food", "Transport", "Rent", "Utilities", "Entertainment",
              "Health", "Education", "Salary", "Other"]


class FinanceError(Exception):
    """Base error for the app."""


class InvalidTransactionError(FinanceError):
    pass


@dataclass
class Transaction:
    id: int
    kind: str          # "income" | "expense"
    amount: float
    category: str
    description: str
    day: str           # ISO date

    def validate(self) -> None:
        if self.kind not in ("income", "expense"):
            raise InvalidTransactionError("kind must be 'income' or 'expense'")
        if self.amount <= 0:
            raise InvalidTransactionError("amount must be positive")
        try:
            datetime.strptime(self.day, "%Y-%m-%d")
        except ValueError:
            raise InvalidTransactionError("date must be YYYY-MM-DD")


class FinanceManager:
    def __init__(self, path: str = DATA_FILE):
        self.path = path
        self.transactions: list[Transaction] = []
        self._next_id = 1

    # ---- CRUD ----
    def add(self, kind, amount, category, description="", day=None) -> Transaction:
        t = Transaction(self._next_id, kind, float(amount), category,
                        description, day or date.today().isoformat())
        t.validate()
        self.transactions.append(t)
        self._next_id += 1
        return t

    def delete(self, tid: int) -> bool:
        before = len(self.transactions)
        self.transactions = [t for t in self.transactions if t.id != tid]
        return len(self.transactions) < before

    # ---- queries ----
    def search(self, keyword="", category=None, kind=None):
        kw = keyword.lower()
        return [t for t in self.transactions
                if kw in t.description.lower()
                and (category is None or t.category == category)
                and (kind is None or t.kind == kind)]

    def balance(self) -> float:
        return sum(t.amount if t.kind == "income" else -t.amount
                   for t in self.transactions)

    def monthly_summary(self, year: int, month: int) -> dict:
        prefix = f"{year:04d}-{month:02d}"
        income = expense = 0.0
        by_cat = defaultdict(float)
        for t in self.transactions:
            if t.day.startswith(prefix):
                if t.kind == "income":
                    income += t.amount
                else:
                    expense += t.amount
                    by_cat[t.category] += t.amount
        return {"income": income, "expense": expense, "net": income - expense,
                "by_category": dict(sorted(by_cat.items(), key=lambda x: -x[1]))}

    # ---- persistence ----
    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in self.transactions], f, indent=2)

    def load(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                self.transactions = [Transaction(**d) for d in json.load(f)]
        except (json.JSONDecodeError, TypeError) as e:
            raise FinanceError(f"Corrupt data file: {e}")
        self._next_id = max((t.id for t in self.transactions), default=0) + 1


# ---------------- CLI ----------------
def _ask_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Please enter a number.")


def _print(ts):
    if not ts:
        print("  (none)")
    for t in ts:
        sign = "+" if t.kind == "income" else "-"
        print(f"  #{t.id:<3} {t.day}  {sign}{t.amount:>10.2f}  {t.category:<13} {t.description}")


def main():
    fm = FinanceManager()
    try:
        fm.load()
    except FinanceError as e:
        print(e)
    menu = """
=== Personal Finance Manager ===
1. Add income      2. Add expense     3. List all
4. Search          5. Monthly summary 6. Balance
7. Delete          8. Save & quit
"""
    while True:
        print(menu)
        c = input("Choice: ").strip()
        try:
            if c in ("1", "2"):
                kind = "income" if c == "1" else "expense"
                print("Categories:", ", ".join(CATEGORIES))
                cat = input("Category: ").strip().title() or "Other"
                amt = _ask_float("Amount: ")
                desc = input("Description: ")
                d = input("Date (YYYY-MM-DD, blank=today): ").strip() or None
                fm.add(kind, amt, cat, desc, d)
                print("Added.")
            elif c == "3":
                _print(fm.transactions)
            elif c == "4":
                kw = input("Keyword: ")
                cat = input("Category (blank=any): ").strip().title() or None
                _print(fm.search(kw, cat))
            elif c == "5":
                y = int(input("Year: ")); m = int(input("Month: "))
                s = fm.monthly_summary(y, m)
                print(f"  Income {s['income']:.2f} | Expense {s['expense']:.2f} | Net {s['net']:.2f}")
                for k, v in s["by_category"].items():
                    print(f"    {k:<13}{v:>10.2f}")
            elif c == "6":
                print(f"  Balance: {fm.balance():.2f}")
            elif c == "7":
                print("Deleted." if fm.delete(int(input("ID: "))) else "Not found.")
            elif c == "8":
                fm.save(); print("Saved. Bye!"); break
            else:
                print("Invalid choice.")
        except (FinanceError, ValueError) as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
