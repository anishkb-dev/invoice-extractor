"""Render the 1280x769 gig image from the real demo output (invoices.xlsx)."""
import sys
from pathlib import Path
import openpyxl
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent.parent
rows = list(openpyxl.load_workbook(root / "invoices.xlsx")["Invoices"].iter_rows(values_only=True))[1:]
H = "/System/Library/Fonts/HelveticaNeue.ttc"
f = lambda s, b=False: ImageFont.truetype(H, s, index=1 if b else 0)
BG, GREEN, WHITE = (15, 42, 36), (110, 231, 183), (255, 255, 255)

im = Image.new("RGB", (1280, 769), BG)
d = ImageDraw.Draw(im)
d.text((60, 140), "PDF invoices", font=f(64, True), fill=WHITE)
d.text((60, 215), "to Excel", font=f(64, True), fill=GREEN)
d.text((60, 290), "with AI, and every error flagged", font=f(30), fill=(200, 220, 212))
for i, t in enumerate(["Vendor, dates, totals, line items", "Any invoice layout, no templates",
                       "Maths checked: lines, subtotal, tax", "Private local AI option"]):
    yy = 370 + i * 44; d.line([(62, yy + 15), (70, yy + 23), (84, yy + 7)], fill=GREEN, width=4); d.text((98, yy), t, font=f(26), fill=WHITE)
for x, (t, c) in zip((60, 150), [("PDF", (220, 70, 60)), ("EXCEL", (33, 150, 83))]):
    w = d.textlength(t, font=f(18, True)) + 28
    d.rounded_rectangle((x, 580, x + w, 616), 8, fill=c); d.text((x + 14, 588), t, font=f(18, True), fill=WHITE)

# spreadsheet card built from real output
X, Y, W = 560, 150, 680
cols = [("Vendor", 200), ("Invoice #", 140), ("Total", 145), ("Status", 160)]
d.rounded_rectangle((X, Y, X + W, Y + 470), 14, fill=WHITE)
d.text((X + 24, Y + 20), "invoices.xlsx", font=f(20, True), fill=(30, 30, 30))
ty = Y + 70
d.rectangle((X + 20, ty, X + W - 20, ty + 40), fill=(232, 240, 236))
cx = X + 30
for name, w in cols:
    d.text((cx, ty + 10), name, font=f(18, True), fill=(40, 40, 40)); cx += w
for r in rows:
    ty += 50
    bad = r[9] != "OK"
    if bad:
        d.rectangle((X + 20, ty - 5, X + W - 20, ty + 40), fill=(248, 215, 218))
    cx = X + 30
    for v, (_, w) in zip([r[1][:20], r[2], f"{r[5]} {r[8]:,.2f}", r[9]], cols):
        d.text((cx, ty + 6), str(v), font=f(18, bad and v == r[9]), fill=(170, 30, 40) if bad and v == r[9] else (50, 50, 50)); cx += w
issue = next(r[10] for r in rows if r[9] != "OK")
d.rounded_rectangle((X + 20, ty + 70, X + W - 20, ty + 160), 10, outline=(220, 80, 90), width=2)
d.text((X + 40, ty + 84), "Why it needs review:", font=f(18, True), fill=(170, 30, 40))
d.text((X + 40, ty + 116), issue, font=f(18), fill=(60, 60, 60))
d.text((X + 24, Y + 430), "Real output from the demo on sample invoices", font=f(15), fill=(110, 110, 110))
im.save(sys.argv[1] if len(sys.argv) > 1 else root / "assets" / "gig-image.png")
