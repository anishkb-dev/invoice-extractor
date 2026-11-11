"""Extract invoice fields from PDFs into an Excel workbook, and flag invoices whose numbers don't add up.

usage: python extract.py samples/*.pdf -o invoices.xlsx
"""
import argparse
import json
import os
from pathlib import Path

import openpyxl
import pymupdf
from openai import OpenAI
from openpyxl.styles import Font, PatternFill

llm = OpenAI(base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
             api_key=os.getenv("LLM_API_KEY", "not-needed-for-local"))
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

PROMPT = """Extract this invoice into JSON with exactly these keys:
vendor, invoice_number, invoice_date (YYYY-MM-DD), due_date (YYYY-MM-DD), currency (ISO code),
subtotal, tax, total (numbers, no symbols or commas),
line_items: list of {{description, quantity, unit_price, amount}}.
Copy values exactly as printed. Use null for anything not on the invoice. Do not calculate or correct anything.

Invoice text:
{text}"""

FIELDS = ["vendor", "invoice_number", "invoice_date", "due_date", "currency", "subtotal", "tax", "total"]


def extract(pdf: Path) -> dict:
    with pymupdf.open(pdf) as doc:
        text = "\n".join(p.get_text() for p in doc)
    r = llm.chat.completions.create(model=MODEL, temperature=0, response_format={"type": "json_object"},
                                    messages=[{"role": "user", "content": PROMPT.format(text=text)}])
    data = json.loads(r.choices[0].message.content)
    data["file"] = pdf.name
    data["issues"] = check(data)
    return data


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def check(d: dict) -> list[str]:
    """Arithmetic checks done in code, not by the LLM: this is what catches extraction and billing errors."""
    issues = [f"missing {k}" for k in FIELDS if d.get(k) in (None, "")]
    items = d.get("line_items") or []
    for i, it in enumerate(items, 1):
        q, p, a = num(it.get("quantity")), num(it.get("unit_price")), num(it.get("amount"))
        if None not in (q, p, a) and abs(q * p - a) > 0.01:
            issues.append(f"line {i}: {q} x {p} != {a}")
    sub, tax, total = num(d.get("subtotal")), num(d.get("tax")), num(d.get("total"))
    amounts = [num(it.get("amount")) for it in items]
    if sub is not None and items and None not in amounts and abs(sum(amounts) - sub) > 0.01:
        issues.append(f"line items sum to {sum(amounts):.2f}, subtotal says {sub:.2f}")
    if None not in (sub, tax, total) and abs(sub + tax - total) > 0.01:
        issues.append(f"subtotal + tax = {sub + tax:.2f}, total says {total:.2f}")
    return issues


def write_xlsx(rows: list[dict], out: Path):
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = "Invoices"
    ws.append(["file", *FIELDS, "status", "issues"])
    red = PatternFill("solid", fgColor="F8D7DA")
    for d in rows:
        ws.append([d["file"], *[d.get(k) for k in FIELDS], "NEEDS REVIEW" if d["issues"] else "OK", "; ".join(d["issues"])])
        if d["issues"]:
            for cell in ws[ws.max_row]:
                cell.fill = red
    li = wb.create_sheet("Line items")
    li.append(["file", "invoice_number", "description", "quantity", "unit_price", "amount"])
    for d in rows:
        for it in d.get("line_items") or []:
            li.append([d["file"], d.get("invoice_number"), it.get("description"), it.get("quantity"), it.get("unit_price"), it.get("amount")])
    for sheet in (ws, li):
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        for col in sheet.columns:
            sheet.column_dimensions[col[0].column_letter].width = min(45, max(len(str(c.value or "")) for c in col) + 2)
    wb.save(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=Path("invoices.xlsx"))
    a = ap.parse_args()
    rows = []
    for p in a.pdfs:
        d = extract(p)
        print(f"{p.name}: {'NEEDS REVIEW - ' + '; '.join(d['issues']) if d['issues'] else 'OK'}")
        rows.append(d)
    write_xlsx(rows, a.out)
    print("wrote", a.out)
