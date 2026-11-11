"""Offline check of the arithmetic validator (no LLM). Run: python test_check.py"""
from extract import check

good = dict(vendor="V", invoice_number="1", invoice_date="2026-01-01", due_date="2026-02-01", currency="USD",
            subtotal=100, tax=10, total=110, line_items=[dict(quantity=2, unit_price=50, amount=100)])
assert check(good) == [], check(good)
assert any("total says" in i for i in check({**good, "total": 120}))
assert any("line 1" in i for i in check({**good, "line_items": [dict(quantity=2, unit_price=50, amount=90)]}))
assert any("sum to" in i for i in check({**good, "subtotal": 95, "total": 105}))
assert "missing due_date" in check({**good, "due_date": None})
print("ok")
