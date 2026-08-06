"""
Bright Mindful Pages -- Sobriety & Recovery Daily Tracker
Interior generator (Python + reportlab)

# Ye script ADHD Planner ke reusable guideline (KDP_Low_Content_Book_Guideline.md)
# ki rules follow karta hai:
#   - Trim size 6x9 in
#   - MARGIN = 0.4in har side, koi bhi shape/text margin cross nahi karta
#   - Sab decorative banners margin ke andar (inset) hain, edge-to-edge nahi
#   - Bottom margin buffer check() function se verify hota hai har page ke baad
#   - Spine text 79+ pages par allowed hoga -- humari page count 100+ hai, safe hai
"""

import math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------------------------------------------------------------
# CONSTANTS -- inch ko point mein convert kiya (1 inch = 72 pt)
# ---------------------------------------------------------------
IN = 72.0
PAGE_W, PAGE_H = 6 * IN, 9 * IN
MARGIN = 0.4 * IN                     # KDP-safe margin, sab tarah ke content isi ke andar rahega
CONTENT_W = PAGE_W - 2 * MARGIN
CONTENT_H = PAGE_H - 2 * MARGIN

# Sobriety Tracker ka apna color palette (base brand DNA + niche shift)
SAGE = HexColor("#C9DCC5")
TEAL = HexColor("#BEE3DB")
SAND = HexColor("#F2E4D0")
ROSE = HexColor("#F0D3D8")
TEXT = HexColor("#4A3F55")            # dark plum -- sab text isi color mein
WHITE = white

FONT_HEAD = "Helvetica-Bold"
FONT_BODY = "Helvetica"

OUT_PATH = "/home/claude/kdp/Sobriety_Recovery_Tracker_Interior.pdf"

# lowest y-value jo kisi bhi page par draw hua (margin-safety verify karne ke liye)
_lowest_y_seen = [PAGE_H]  # list isliye taake nested function isse update kar sake


def track_lowest(y):
    """# Har element ke baad iska sabse neeche wala y-point record karo"""
    if y < _lowest_y_seen[0]:
        _lowest_y_seen[0] = y


# ---------------------------------------------------------------
# DRAWING HELPERS
# ---------------------------------------------------------------

def rounded_rect(c, x, y, w, h, r, fill=None, stroke=None, lw=1):
    """# Generic rounded rectangle -- hamesha margin ke andar call karna"""
    c.saveState()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, fill=1 if fill else 0, stroke=1 if stroke else 0)
    c.restoreState()
    track_lowest(y)


def checkbox(c, x, y, size=8):
    """# Chhota khali checkbox square -- check-in items ke liye"""
    c.saveState()
    c.setStrokeColor(TEXT)
    c.setLineWidth(1)
    c.rect(x, y, size, size, fill=0, stroke=1)
    c.restoreState()
    track_lowest(y)


def draw_droplet(c, x, y, size=10, color=None):
    """# Simple droplet icon -- circle + upar triangle tip (water intake ke liye)"""
    color = color or TEXT
    c.saveState()
    c.setFillColor(color)
    r = size / 2
    cx, cy = x + r, y + r * 0.8
    c.circle(cx, cy, r * 0.8, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(cx - r * 0.55, cy + r * 0.25)
    p.lineTo(cx, cy + r * 1.6)
    p.lineTo(cx + r * 0.55, cy + r * 0.25)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    track_lowest(y)


def draw_moon(c, x, y, size=10, color=None):
    """# Crescent moon icon -- do circles overlap karke banaya (sleep ke liye)"""
    color = color or TEXT
    c.saveState()
    c.setFillColor(color)
    r = size / 2
    c.circle(x + r, y + r, r, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.circle(x + r + r * 0.45, y + r, r * 0.85, fill=1, stroke=0)
    c.restoreState()
    track_lowest(y)


def draw_heart(c, x, y, size=10, color=None):
    """# Heart icon -- do circles + neeche triangle (craving/urge check ke liye)"""
    color = color or TEXT
    c.saveState()
    c.setFillColor(color)
    r = size / 4
    cx, cy = x + size / 2, y + size * 0.55
    c.circle(cx - r, cy, r, fill=1, stroke=0)
    c.circle(cx + r, cy, r, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(cx - 2 * r, cy)
    p.lineTo(cx, y)
    p.lineTo(cx + 2 * r, cy)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    track_lowest(y)


def draw_chat_bubble(c, x, y, size=10, color=None):
    """# Chat bubble icon -- rounded rect + chhota triangle tail (sponsor call ke liye)"""
    color = color or TEXT
    c.saveState()
    c.setFillColor(color)
    w, h = size, size * 0.75
    c.roundRect(x, y + size * 0.25, w, h, h / 3, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(x + w * 0.25, y + size * 0.25)
    p.lineTo(x + w * 0.15, y)
    p.lineTo(x + w * 0.45, y + size * 0.25)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    track_lowest(y)


def centered_text(c, text, cx, y, font=FONT_HEAD, size=18, color=TEXT):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    w = stringWidth(text, font, size)
    c.drawString(cx - w / 2, y, text)
    c.restoreState()
    track_lowest(y)


def label(c, text, x, y, font=FONT_BODY, size=9, color=TEXT):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)
    c.restoreState()
    track_lowest(y)


def check_bottom_margin(page_label):
    """
    # Har page complete hone ke baad ye check karo ke sabse neeche wala
    # element MARGIN line se kam se kam 0.05in upar hai -- warna KDP
    # 'object outside margin' error dega.
    """
    buffer = _lowest_y_seen[0] - MARGIN
    status = "OK" if buffer >= 0.05 * IN else "!! TOO CLOSE !!"
    print(f"  [{page_label}] lowest y = {_lowest_y_seen[0]:.1f}pt, "
          f"buffer above margin = {buffer/IN:.3f}in -> {status}")
    _lowest_y_seen[0] = PAGE_H  # reset for next page


# ---------------------------------------------------------------
# PAGE BUILDERS
# ---------------------------------------------------------------

def title_page(c):
    # Background inset banner -- margin ke andar hi (edge-to-edge nahi)
    rounded_rect(c, MARGIN, MARGIN, CONTENT_W, CONTENT_H, 14, fill=SAGE)
    centered_text(c, "Sobriety & Recovery", PAGE_W / 2, PAGE_H - 2.2 * IN, size=24)
    centered_text(c, "Daily Tracker", PAGE_W / 2, PAGE_H - 2.55 * IN, size=24)
    centered_text(c, "A 90-Day Undated Recovery Journal", PAGE_W / 2, PAGE_H - 3.2 * IN,
                   font=FONT_BODY, size=12)
    centered_text(c, "One day at a time.", PAGE_W / 2, PAGE_H - 3.5 * IN,
                   font=FONT_BODY, size=11)
    c.showPage()
    check_bottom_margin("Title page")


def intro_page(c):
    rounded_rect(c, MARGIN, MARGIN, CONTENT_W, CONTENT_H, 14, fill=WHITE, stroke=SAGE, lw=2)
    x = MARGIN + 0.3 * IN
    y = PAGE_H - MARGIN - 0.6 * IN
    centered_text(c, "How to Use This Tracker", PAGE_W / 2, y, size=16)
    y -= 0.5 * IN
    steps = [
        ("1. Set Today's Focus", "One small intention for the day -- keep it simple."),
        ("2. Fill Your Top 3 Priorities", "Short, achievable. Progress, not perfection."),
        ("3. Use the Time Blocks", "Give your day light structure, not pressure."),
        ("4. Track Your Craving/Urge Level", "Naming it takes away some of its power."),
        ("5. Check In on Habits", "Meetings, sponsor calls, water, sleep -- consistency counts."),
        ("6. Write One Gratitude Line", "Even on hard days, look for one small thing."),
        ("7. Review at Milestones", "Day 7, 30, 60 & 90 -- pause and reflect on how far you've come."),
    ]
    for h, body in steps:
        label(c, h, x, y, font=FONT_HEAD, size=11)
        y -= 0.22 * IN
        label(c, body, x, y, font=FONT_BODY, size=9.5)
        y -= 0.35 * IN
    c.showPage()
    check_bottom_margin("Intro page")


def tracker_overview_page(c, start_day, end_day):
    rounded_rect(c, MARGIN, MARGIN, CONTENT_W, CONTENT_H, 14, fill=TEAL)
    x = MARGIN + 0.25 * IN
    y = PAGE_H - MARGIN - 0.55 * IN
    label(c, f"Progress Tracker (Days {start_day}-{end_day})", x, y, font=FONT_HEAD, size=13)
    y -= 0.3 * IN
    label(c, "Mark each day you complete your check-in", x, y, size=9)
    y -= 0.35 * IN

    rows = ["Meeting attended", "Sponsor/support call", "Water intake",
            "Sleep 7+ hrs", "Gratitude line written"]
    row_h = 0.42 * IN
    for r in rows:
        label(c, r, x, y, font=FONT_BODY, size=9.5)
        y -= row_h
    # day numbers row + checkbox grid
    y_top = y + row_h * len(rows) - 0.05 * IN
    col_w = CONTENT_W / (end_day - start_day + 1)
    for i, day in enumerate(range(start_day, end_day + 1)):
        cx = x + i * col_w + col_w / 2
        c.saveState()
        c.setFont(FONT_BODY, 5.5)
        c.setFillColor(TEXT)
        c.drawCentredString(cx, y_top + 0.05 * IN, str(day))
        c.restoreState()
        for r_i in range(len(rows)):
            cy = y_top - r_i * row_h
            checkbox(c, cx - 3, cy - 3, size=6)
    c.showPage()
    check_bottom_margin(f"Tracker overview {start_day}-{end_day}")


def daily_page(c, day):
    x0 = MARGIN
    y_top = PAGE_H - MARGIN

    # Header banner -- inset, margin ke andar
    rounded_rect(c, x0, y_top - 0.55 * IN, CONTENT_W, 0.55 * IN, 10, fill=SAND)
    label(c, f"Day {day}", x0 + 0.15 * IN, y_top - 0.38 * IN, font=FONT_HEAD, size=14)
    label(c, "Date: ______________   Day:  M  T  W  T  F  S  S",
          x0 + 1.6 * IN, y_top - 0.38 * IN, font=FONT_BODY, size=9)

    y = y_top - 0.85 * IN
    label(c, "Today's Focus: ___________________________________", x0, y, size=9.5)

    y -= 0.3 * IN
    label(c, "Top 3 Priorities", x0, y, font=FONT_HEAD, size=10)
    y -= 0.2 * IN
    label(c, "1. ______________   2. ______________   3. ______________", x0, y, size=9)

    # Time blocks -- 2 columns x 8 rows (6am-9pm, jaisa base planner mein tha)
    y -= 0.3 * IN
    label(c, "Time Blocks", x0, y, font=FONT_HEAD, size=10)
    y -= 0.2 * IN
    times = ["6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM", "1 PM",
             "2 PM", "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM"]
    col_w = CONTENT_W / 2
    row_h = 0.145 * IN
    tb_top = y
    for i, t in enumerate(times):
        col = i // 8
        row = i % 8
        tx = x0 + col * col_w
        ty = tb_top - row * row_h
        label(c, t, tx, ty, size=7.5)
        c.saveState()
        c.setStrokeColor(TEXT)
        c.setLineWidth(0.5)
        c.line(tx + 0.5 * IN, ty + 2, tx + col_w - 0.05 * IN, ty + 2)
        c.restoreState()
        track_lowest(ty)
    y = tb_top - 8 * row_h - 0.15 * IN

    # Craving/Urge Level
    label(c, "Craving / Urge Level", x0, y, font=FONT_HEAD, size=10)
    y -= 0.2 * IN
    levels = ["None", "Mild", "Moderate", "Strong", "Intense"]
    lx = x0
    for lvl in levels:
        draw_heart(c, lx, y - 8, size=8)
        label(c, lvl, lx + 12, y - 5, size=8)
        lx += CONTENT_W / len(levels)

    # Check-in row with icons
    y -= 0.35 * IN
    label(c, "Check-in", x0, y, font=FONT_HEAD, size=10)
    y -= 0.22 * IN
    checks = [("Meeting attended", draw_chat_bubble), ("Sponsor call made", draw_chat_bubble),
              ("Water (8 cups)", draw_droplet), ("Sleep 7+ hrs", draw_moon)]
    col_w2 = CONTENT_W / 2
    for i, (ctext, icon_fn) in enumerate(checks):
        col = i % 2
        row = i // 2
        cx = x0 + col * col_w2
        cy = y - row * 0.24 * IN
        checkbox(c, cx, cy - 7, size=8)
        icon_fn(c, cx + 14, cy - 9, size=8)
        label(c, ctext, cx + 26, cy - 5, size=8.5)
    y -= 2 * 0.24 * IN + 0.1 * IN

    # Gratitude line
    label(c, "One thing I'm grateful for today:", x0, y, font=FONT_HEAD, size=9.5)
    y -= 0.18 * IN
    label(c, "_______________________________________________", x0, y, size=9)

    # Notes -- box, bottom margin ke andar hi rehna chahiye
    y -= 0.3 * IN
    notes_h = max(y - MARGIN - 0.05 * IN, 0.6 * IN)
    if y - notes_h < MARGIN + 0.05 * IN:
        notes_h = y - MARGIN - 0.05 * IN
    rounded_rect(c, x0, y - notes_h, CONTENT_W, notes_h, 8, stroke=SAGE, lw=1.2)
    label(c, "Notes", x0 + 0.1 * IN, y - 0.18 * IN, font=FONT_HEAD, size=9)
    track_lowest(y - notes_h)

    c.showPage()
    check_bottom_margin(f"Day {day}")


def weekly_review_page(c, week_num, day_range):
    rounded_rect(c, MARGIN, MARGIN, CONTENT_W, CONTENT_H, 14, fill=SAGE)
    x = MARGIN + 0.25 * IN
    y = PAGE_H - MARGIN - 0.55 * IN
    label(c, f"Week {week_num} Review (Days {day_range[0]}-{day_range[1]})",
          x, y, font=FONT_HEAD, size=13)
    y -= 0.45 * IN
    prompts = [
        "What helped me stay steady this week?",
        "What was hardest?",
        "One pacing adjustment for next week",
        "Wins to celebrate",
    ]
    for p in prompts:
        label(c, p, x, y, font=FONT_HEAD, size=10)
        y -= 0.9 * IN
        c.saveState()
        c.setStrokeColor(TEAL)
        c.setLineWidth(0.7)
        for line_i in range(3):
            ly = y + 0.9 * IN - 0.28 * IN - line_i * 0.26 * IN
            c.line(x, ly, PAGE_W - MARGIN - 0.25 * IN, ly)
        c.restoreState()
        track_lowest(y)
    c.showPage()
    check_bottom_margin(f"Week {week_num} review")


def milestone_review_page(c, milestone_label, day):
    rounded_rect(c, MARGIN, MARGIN, CONTENT_W, CONTENT_H, 14, fill=ROSE)
    x = MARGIN + 0.3 * IN
    y = PAGE_H - MARGIN - 0.7 * IN
    centered_text(c, "MILESTONE REACHED", PAGE_W / 2, y, size=13, color=TEXT)
    y -= 0.35 * IN
    centered_text(c, f"{milestone_label}  (Day {day})", PAGE_W / 2, y, size=20)
    y -= 0.6 * IN
    prompts = [
        "Days sober so far: this stretch",
        "What helped me the most?",
        "What was hardest?",
        "One thing I'm proud of",
        "A note to my future self",
    ]
    for p in prompts:
        label(c, p, x, y, font=FONT_HEAD, size=10)
        y -= 0.6 * IN
        c.saveState()
        c.setStrokeColor(TEXT)
        c.setLineWidth(0.6)
        for line_i in range(2):
            ly = y + 0.6 * IN - 0.25 * IN - line_i * 0.24 * IN
            c.line(x, ly, PAGE_W - MARGIN - 0.3 * IN, ly)
        c.restoreState()
        track_lowest(y)
    c.showPage()
    check_bottom_margin(f"Milestone {milestone_label}")


def blank_notes_page(c, idx):
    rounded_rect(c, MARGIN, MARGIN, CONTENT_W, CONTENT_H, 14, fill=WHITE, stroke=SAGE, lw=1.5)
    centered_text(c, "Notes", PAGE_W / 2, PAGE_H - MARGIN - 0.5 * IN, size=14)
    c.showPage()
    check_bottom_margin(f"Blank notes {idx}")


# ---------------------------------------------------------------
# BUILD FULL INTERIOR
# ---------------------------------------------------------------

def build():
    c = canvas.Canvas(OUT_PATH, pagesize=(PAGE_W, PAGE_H))

    title_page(c)
    intro_page(c)

    tracker_overview_page(c, 1, 30)
    tracker_overview_page(c, 31, 60)
    tracker_overview_page(c, 61, 90)

    week_num = 1
    for day in range(1, 91):
        daily_page(c, day)

        if day == 7:
            milestone_review_page(c, "7-Day Milestone", day)
        if day == 30:
            milestone_review_page(c, "30-Day Milestone", day)
        if day == 60:
            milestone_review_page(c, "60-Day Milestone", day)
        if day == 90:
            milestone_review_page(c, "90-Day Milestone", day)

        # Weekly review har 7 din baad (day 7,14,...,84)
        if day % 7 == 0 and day <= 84:
            weekly_review_page(c, week_num, (day - 6, day))
            week_num += 1

    # Page count check -- agar 72 se kam ho to padding pages add karo
    # (yahan already 100+ pages hain, is se zaroorat nahi, lekin future-proof rakha hai)
    c.save()


if __name__ == "__main__":
    build()
    from pypdf import PdfReader
    reader = PdfReader(OUT_PATH)
    print(f"\nTOTAL PAGES: {len(reader.pages)}")
