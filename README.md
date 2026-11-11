# Invoice Extractor

Turn a folder of PDF invoices into one clean Excel workbook, and **flag every invoice whose numbers don't add up**.

- Pulls vendor, invoice number, dates, currency, subtotal, tax, total and every line item
- Works on different invoice layouts, with no templates to set up
- **Checks the maths in code, not with the AI**: qty × price per line, line items vs subtotal, subtotal + tax vs total, missing fields
- Problem invoices are highlighted red with the exact reason, e.g. `subtotal + tax = 3264.00, total says 3400.00`
- Any LLM: OpenAI, Groq, or a local model through Ollama (invoices never leave your machine)

```
$ python extract.py samples/*.pdf -o invoices.xlsx
invoice_1_acme.pdf: OK
invoice_2_northwind.pdf: OK
invoice_3_brightline.pdf: NEEDS REVIEW - subtotal + tax = 3264.00, total says 3400.00
wrote invoices.xlsx
```

Output: an `Invoices` sheet (one row per invoice, with status) and a `Line items` sheet.
Tested with a local 7B model (Qwen2.5-7B): all fields and line items on the sample invoices extracted correctly, and the overbilled invoice was caught.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && set -a; source .env; set +a   # choose your LLM provider
python samples/make_invoices.py                        # 3 fictional sample invoices
python extract.py samples/*.pdf -o invoices.xlsx
python test_check.py                                   # offline test of the validation logic
```

## Next steps for production

OCR for scanned/photographed invoices, Google Sheets or QuickBooks/Xero export, watching an email inbox or Drive folder, and duplicate-invoice detection.
