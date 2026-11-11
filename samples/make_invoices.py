"""Generate 3 fictional invoices in different layouts. invoice_3 has a deliberate total error."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT = Path(__file__).parent

INVOICES = [
    dict(file="invoice_1_acme.pdf", vendor="Acme Office Supplies Ltd", number="INV-2026-0412", date="2026-10-03",
         due="2026-11-02", currency="USD", tax_rate=0.08,
         items=[("A4 paper, box of 5 reams", 12, 24.50), ("Toner cartridge HP 58A", 4, 89.00), ("Desk organiser", 6, 15.25)]),
    dict(file="invoice_2_northwind.pdf", vendor="Northwind Cloud Services", number="NW-88317", date="2026-10-15",
         due="2026-10-30", currency="EUR", tax_rate=0.19,
         items=[("Managed hosting, October", 1, 1450.00), ("Extra storage 500 GB", 2, 60.00)]),
    dict(file="invoice_3_brightline.pdf", vendor="Brightline Marketing Co.", number="BL/2026/077", date="2026-10-21",
         due="2026-11-20", currency="GBP", tax_rate=0.20,
         items=[("Social media campaign", 1, 2200.00), ("Copywriting, 8 hours", 8, 65.00)], wrong_total=3400.00),
]


def draw(inv):
    c = canvas.Canvas(str(OUT / inv["file"]), pagesize=A4)
    w, h = A4
    if inv["file"].startswith("invoice_2"):  # different layout: header block on the right
        c.setFont("Helvetica-Bold", 18); c.drawRightString(w - 50, h - 60, inv["vendor"])
        c.setFont("Helvetica", 10)
        c.drawRightString(w - 50, h - 80, f"Invoice no. {inv['number']}  |  Issued {inv['date']}  |  Payment due {inv['due']}")
    else:
        c.setFont("Helvetica-Bold", 22); c.drawString(50, h - 60, "INVOICE")
        c.setFont("Helvetica", 11); c.drawString(50, h - 85, inv["vendor"])
        c.drawString(350, h - 60, f"Invoice #: {inv['number']}")
        c.drawString(350, h - 75, f"Date: {inv['date']}")
        c.drawString(350, h - 90, f"Due date: {inv['due']}")
    y = h - 150
    c.setFont("Helvetica-Bold", 10)
    for x, t in [(50, "Description"), (330, "Qty"), (400, "Unit price"), (490, "Amount")]:
        c.drawString(x, y, t)
    c.setFont("Helvetica", 10)
    subtotal = 0
    for desc, qty, price in inv["items"]:
        y -= 18
        amt = qty * price; subtotal += amt
        c.drawString(50, y, desc); c.drawString(330, y, str(qty))
        c.drawString(400, y, f"{price:,.2f}"); c.drawString(490, y, f"{amt:,.2f}")
    tax = round(subtotal * inv["tax_rate"], 2)
    total = inv.get("wrong_total", subtotal + tax)
    y -= 40
    for label, val in [("Subtotal", subtotal), (f"Tax ({inv['tax_rate']:.0%})", tax), (f"Total ({inv['currency']})", total)]:
        c.drawString(400, y, label); c.drawString(490, y, f"{val:,.2f}"); y -= 16
    c.save()


if __name__ == "__main__":
    for inv in INVOICES:
        draw(inv)
    print("wrote", len(INVOICES), "invoices to", OUT)
