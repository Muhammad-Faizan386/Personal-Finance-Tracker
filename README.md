# 🧾 Personal Finance Manager
**Course proof:** Programming (Python fundamentals, OOP, file handling, exceptions)

A command-line app to track income/expenses, search, and produce monthly summaries.

## Run
```bash
python finance.py
python -m unittest discover tests
```

## Concepts demonstrated
| Concept | Where |
|---|---|
| Variables / types | `Transaction` dataclass |
| Functions, loops, conditionals | CLI `main()` loop |
| OOP | `FinanceManager`, `Transaction` |
| File handling | `save()` / `load()` JSON |
| Exception handling | custom `FinanceError` hierarchy, input validation |
| Modules | `json`, `dataclasses`, `datetime`, `collections` |
| Testing | `tests/test_finance.py` |

## Resume bullet
> Built a Python CLI finance tracker with OOP design, JSON persistence, custom exceptions and unit tests.
