#!/usr/bin/env python3
"""
KDP Low-Content Book Interior Generator
Generates a KDP-compliant interior PDF using reportlab.

Usage: python3 generate_book.py '<json_config>' <output_path>
"""

import sys
import json
import math
import os

from reportlab.lib.pagesizes import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas as rl_canvas

# ── Page dimensions ──────────────────────────────────────────────────────────
PAGE_W = 6 * inch
PAGE_H = 9 * inch
MARGIN = 0.4 * inch  # KDP-safe margin – NEVER let anything touch x=0,y=0,PAGE_W,PAGE_H

# Inner content box
INNER_X = MARGIN
INNER_Y = MARGIN
INNER_W = PAGE_W - 2 * MARGIN
INNER_H = PAGE_H - 2 * MARGIN
INNER_TOP = PAGE_H - MARGIN  # top edge of content area

# ── Color palettes ────────────────────────────────────────────────────────────
PALETTES = {
    "lavender_mint": {
        "primary": HexColor("#E6D9F7"),    # lavender
        "secondary": HexColor("#D6F3E8"),  # mint
        "accent": HexColor("#FBD6E3"),     # pink
        "highlight": HexColor("#D9EEFB"),  # sky blue
        "text": HexColor("#4A3F55"),
        "line": HexColor("#C4B8D4"),
        "header_text": HexColor("#6B5580"),
    },
    "ocean_peach": {
        "primary": HexColor("#D9EEFB"),
        "secondary": HexColor("#FFE3D1"),
        "accent": HexColor("#B8D8F0"),
        "highlight": HexColor("#FFDFC4"),
        "text": HexColor("#2D4A5E"),
        "line": HexColor("#A8C8E0"),
        "header_text": HexColor("#2D6080"),
    },
    "sky_pink": {
        "primary": HexColor("#FBD6E3"),
        "secondary": HexColor("#D9EEFB"),
        "accent": HexColor("#E6D9F7"),
        "highlight": HexColor("#FFE3D1"),
        "text": HexColor("#5C2D4E"),
        "line": HexColor("#E0A0BC"),
        "header_text": HexColor("#8B3060"),
    },
    "forest_earth": {
        "primary": HexColor("#D8EAD4"),
        "secondary": HexColor("#F5E6D0"),
        "accent": HexColor("#B8D4C0"),
        "highlight": HexColor("#EAD8C4"),
        "text": HexColor("#2C3E28"),
        "line": HexColor("#8EAA86"),
        "header_text": HexColor("#3A5C34"),
    },
    # BMP-002: Sobriety & Recovery — calm growth palette
    "sage_teal": {
        "primary": HexColor("#C9DCC5"),    # sage green
        "secondary": HexColor("#BEE3DB"),  # soft teal
        "accent": HexColor("#F0D3D8"),     # muted rose (milestone highlights only)
        "highlight": HexColor("#F2E4D0"),  # warm sand
        "text": HexColor("#4A3F55"),
        "line": HexColor("#9ABEA8"),
        "header_text": HexColor("#3A6B50"),
    },
    # BMP-003: Chronic Pain & Fatigue — low-stimulation gentle palette
    "lavender_grey": {
        "primary": HexColor("#E6D9F7"),    # lavender (unchanged)
        "secondary": HexColor("#DCE3EA"),  # soft grey-blue (rest/low-energy)
        "accent": HexColor("#D6F3E8"),     # mint
        "highlight": HexColor("#FFE3D1"),  # peach (used sparingly)
        "text": HexColor("#4A3F55"),
        "line": HexColor("#B0BEC5"),
        "header_text": HexColor("#5A6A8A"),
    },
    "cobalt_coral": {
        "primary": HexColor("#BFDBFE"),
        "secondary": HexColor("#FDA4AF"),
        "accent": HexColor("#FDE68A"),
        "highlight": HexColor("#DBEAFE"),
        "text": HexColor("#172554"),
        "line": HexColor("#93C5FD"),
        "header_text": HexColor("#1D4ED8"),
    },
    "sunshine_mint": {
        "primary": HexColor("#FEF08A"),
        "secondary": HexColor("#A7F3D0"),
        "accent": HexColor("#BAE6FD"),
        "highlight": HexColor("#ECFCCB"),
        "text": HexColor("#14532D"),
        "line": HexColor("#86EFAC"),
        "header_text": HexColor("#166534"),
    },
    "berry_pop": {
        "primary": HexColor("#F9A8D4"),
        "secondary": HexColor("#C4B5FD"),
        "accent": HexColor("#FED7AA"),
        "highlight": HexColor("#FCE7F3"),
        "text": HexColor("#581C87"),
        "line": HexColor("#D8B4FE"),
        "header_text": HexColor("#9D174D"),
    },
    "ocean_lime": {
        "primary": HexColor("#7DD3FC"),
        "secondary": HexColor("#BEF264"),
        "accent": HexColor("#99F6E4"),
        "highlight": HexColor("#DBEAFE"),
        "text": HexColor("#082F49"),
        "line": HexColor("#67E8F9"),
        "header_text": HexColor("#0369A1"),
    },
    "tangerine_sky": {
        "primary": HexColor("#FDBA74"),
        "secondary": HexColor("#7DD3FC"),
        "accent": HexColor("#FEF3C7"),
        "highlight": HexColor("#E0F2FE"),
        "text": HexColor("#172554"),
        "line": HexColor("#93C5FD"),
        "header_text": HexColor("#C2410C"),
    },
}

# ── Helper functions ──────────────────────────────────────────────────────────

def rounded_rect(c, x, y, w, h, radius, fill_color=None, stroke_color=None, stroke_width=0):
    """Draw a filled/stroked rounded rectangle. All coords are inset within page."""
    assert x >= MARGIN - 1 and y >= MARGIN - 1, f"rect too close to edge: x={x}, y={y}"
    assert x + w <= PAGE_W - MARGIN + 1 and y + h <= PAGE_H - MARGIN + 1, \
        f"rect exceeds content area: x+w={x+w}, y+h={y+h}"
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, w, h, radius)
    if fill_color:
        c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_width)
    if fill_color and stroke_color:
        c.drawPath(p, fill=1, stroke=1)
    elif fill_color:
        c.drawPath(p, fill=1, stroke=0)
    elif stroke_color:
        c.drawPath(p, fill=0, stroke=1)
    c.restoreState()


def draw_line(c, x1, y1, x2, y2, color, width=0.5):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def centered_text(c, text, y, font, size, color):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(PAGE_W / 2, y, text)
    c.restoreState()


def write_text(c, text, x, y, font, size, color):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)
    c.restoreState()


def draw_header_band(c, colors, label, page_number=None):
    """Draw a colorful inset header band at top of page."""
    band_h = 0.45 * inch
    band_y = INNER_TOP - band_h
    rounded_rect(c, INNER_X, band_y, INNER_W, band_h, 6,
                 fill_color=colors["primary"])
    write_text(c, label, INNER_X + 10, band_y + 14, "Helvetica-Bold", 11, colors["header_text"])
    if page_number is not None:
        write_text(c, f"Day {page_number}", PAGE_W - MARGIN - 70, band_y + 14,
                   "Helvetica", 10, colors["text"])


def draw_footer_dots(c, colors, page_num, total_pages):
    """Draw a subtle footer with page number, stays inside margin."""
    footer_y = MARGIN + 4  # safely above bottom margin
    write_text(c, str(page_num), PAGE_W / 2 - 10, footer_y, "Helvetica", 7, colors["line"])


# ── Page generators ───────────────────────────────────────────────────────────

def title_page(c, cfg, colors):
    # Background fill (inset, not edge-to-edge)
    rounded_rect(c, INNER_X, INNER_Y, INNER_W, INNER_H, 10,
                 fill_color=colors["primary"])

    # Decorative accent strip
    accent_h = 0.6 * inch
    rounded_rect(c, INNER_X, INNER_TOP - accent_h, INNER_W, accent_h, 8,
                 fill_color=colors["accent"])

    # Title
    topic = cfg.get("topic", "Daily Planner")
    title_parts = topic.split(" ")
    # Try to fit on two lines nicely
    half = max(1, len(title_parts) // 2)
    line1 = " ".join(title_parts[:half])
    line2 = " ".join(title_parts[half:])

    centered_text(c, line1, PAGE_H * 0.60, "Helvetica-Bold", 32, colors["header_text"])
    if line2:
        centered_text(c, line2, PAGE_H * 0.60 - 0.40 * inch, "Helvetica-Bold", 32, colors["header_text"])

    # Subtitle
    subtitle = cfg.get("subtitle") or f"A {cfg.get('dayCount', 60)}-Day Undated Planner"
    centered_text(c, subtitle, PAGE_H * 0.60 - 0.85 * inch, "Helvetica", 13, colors["text"])

    # Decorative dots row
    dot_y = PAGE_H * 0.42
    for i in range(5):
        cx = PAGE_W / 2 - 1.0 * inch + i * 0.5 * inch
        c.saveState()
        c.setFillColor(colors["secondary"])
        c.circle(cx, dot_y, 5, fill=1, stroke=0)
        c.restoreState()

    # Target audience tag
    audience = cfg.get("targetAudience", "Adults")
    tag_text = f"For {audience}"
    tag_w = 2.4 * inch
    tag_h = 0.32 * inch
    tag_x = (PAGE_W - tag_w) / 2
    tag_y = PAGE_H * 0.35
    rounded_rect(c, tag_x, tag_y, tag_w, tag_h, 8, fill_color=colors["secondary"])
    centered_text(c, tag_text, tag_y + 9, "Helvetica", 10, colors["text"])

    # Author
    author = cfg.get("authorName", "Bright Mindful Pages")
    centered_text(c, author, INNER_Y + 22, "Helvetica", 11, colors["text"])
    draw_line(c, INNER_X + 0.3 * inch, INNER_Y + 16, PAGE_W - MARGIN - 0.3 * inch,
              INNER_Y + 16, colors["line"], 0.5)

    c.showPage()


def intro_page(c, cfg, colors):
    niche = cfg.get("niche", "your topic")
    topic = cfg.get("topic", "Daily Planner")
    day_count = cfg.get("dayCount", 60)

    draw_header_band(c, colors, "How to Use This Planner")

    y = INNER_TOP - 0.65 * inch
    write_text(c, "Welcome!", INNER_X, y, "Helvetica-Bold", 15, colors["header_text"])
    y -= 0.22 * inch

    intro_lines = [
        f"This {day_count}-day undated planner is designed to support you",
        f"on your journey with {niche}. There are no dates — start any day,",
        "at your own pace, without the pressure of a fixed calendar.",
        "",
        "Your planner includes:",
    ]
    for line in intro_lines:
        write_text(c, line, INNER_X, y, "Helvetica", 10, colors["text"])
        y -= 0.175 * inch

    features = [
        "  •  A daily spread with space for priorities, notes & reflection",
        "  •  A habit tracker to build consistent routines",
        "  •  Weekly review pages to celebrate progress",
        f"  •  {day_count} days of focused, intentional planning",
        "  •  Undated — start any time, restart any time",
    ]
    y -= 0.05 * inch
    for feat in features:
        rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.24 * inch, 4,
                     fill_color=colors["secondary"])
        write_text(c, feat, INNER_X + 6, y + 2, "Helvetica", 10, colors["text"])
        y -= 0.28 * inch

    y -= 0.12 * inch
    write_text(c, "Tips for success:", INNER_X, y, "Helvetica-Bold", 11, colors["header_text"])
    y -= 0.22 * inch
    tips = [
        "  1.  Fill in your planner the night before or each morning.",
        "  2.  Be honest — this is your private space.",
        "  3.  Celebrate small wins. Progress is progress.",
        "  4.  If you miss a day, just pick back up — no guilt.",
    ]
    for tip in tips:
        write_text(c, tip, INNER_X, y, "Helvetica", 10, colors["text"])
        y -= 0.195 * inch

    c.showPage()


def habit_tracker_page(c, cfg, colors, month_label="Month 1"):
    draw_header_band(c, colors, f"Habit Tracker — {month_label}")

    # Month heading
    y = INNER_TOP - 0.65 * inch
    write_text(c, "Track your habits. Every check mark counts.", INNER_X, y,
               "Helvetica", 10, colors["text"])
    y -= 0.28 * inch

    habits = [
        "Morning routine",
        "Exercise / movement",
        "Water intake",
        "Healthy meal",
        "Medication / supplements",
        "Journaling / reflection",
        "Screen-free time",
        "Quality sleep",
    ]

    # Column headers (days 1-31)
    col_x = INNER_X + 1.55 * inch
    day_col_w = (INNER_W - 1.55 * inch) / 31
    header_y = y
    for d in range(1, 32):
        cx = col_x + (d - 1) * day_col_w + day_col_w / 2
        write_text(c, str(d), cx - 3, header_y, "Helvetica", 6, colors["text"])
    y -= 0.2 * inch

    row_h = 0.28 * inch
    for i, habit in enumerate(habits):
        row_y = y - i * (row_h + 0.04 * inch)
        # Alternate row background
        bg = colors["secondary"] if i % 2 == 0 else colors["primary"]
        rounded_rect(c, INNER_X, row_y, INNER_W, row_h, 4, fill_color=bg)
        # Habit label
        write_text(c, habit, INNER_X + 5, row_y + 9, "Helvetica", 9, colors["text"])
        # Day boxes
        for d in range(31):
            bx = col_x + d * day_col_w + 1
            c.saveState()
            c.setStrokeColor(colors["line"])
            c.setLineWidth(0.4)
            c.rect(bx, row_y + 4, day_col_w - 2, row_h - 8)
            c.restoreState()

    c.showPage()


def daily_page(c, cfg, colors, day_num):
    draw_header_band(c, colors, "My Daily Planner", page_number=day_num)

    y = INNER_TOP - 0.65 * inch

    # Date + mood row
    rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.32 * inch, 6,
                 fill_color=colors["secondary"])
    write_text(c, "Date: _______________", INNER_X + 6, y + 4, "Helvetica", 9, colors["text"])
    write_text(c, "Mood:  😊  😐  😔  😤  😴", INNER_X + 2.2 * inch, y + 4, "Helvetica", 9, colors["text"])
    y -= 0.40 * inch

    def section_label(label, sy):
        rounded_rect(c, INNER_X, sy, 1.4 * inch, 0.22 * inch, 4, fill_color=colors["accent"])
        write_text(c, label, INNER_X + 5, sy + 5, "Helvetica-Bold", 8, colors["header_text"])

    def write_lines(sy, count, line_color, spacing=0.22):
        for i in range(count):
            lx1 = INNER_X
            lx2 = PAGE_W - MARGIN
            ly = sy - i * (spacing * inch)
            draw_line(c, lx1, ly, lx2, ly, line_color, 0.4)
        return sy - count * (spacing * inch) - 0.05 * inch

    # Top 3 Priorities
    section_label("Top 3 Priorities", y)
    y -= 0.28 * inch
    y = write_lines(y, 3, colors["line"], spacing=0.235)

    # Schedule
    y -= 0.05 * inch
    section_label("Schedule / To-Do", y)
    y -= 0.28 * inch
    # Time blocks
    times = ["7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM",
             "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM"]
    time_col_w = 0.55 * inch
    row_h_t = 0.195 * inch
    for i, t in enumerate(times):
        ry = y - i * row_h_t
        if ry < MARGIN + 0.5 * inch:
            break
        bg = colors["secondary"] if i % 2 == 0 else None
        if bg:
            c.saveState()
            c.setFillColor(bg)
            c.rect(INNER_X, ry - row_h_t + 3, INNER_W, row_h_t - 1, fill=1, stroke=0)
            c.restoreState()
        write_text(c, t, INNER_X + 2, ry - row_h_t + 7, "Helvetica", 7.5, colors["text"])
        draw_line(c, INNER_X + time_col_w, ry - row_h_t + 3,
                  PAGE_W - MARGIN, ry - row_h_t + 3, colors["line"], 0.3)

    y -= (len(times) + 1) * row_h_t

    if y < MARGIN + 0.6 * inch:
        c.showPage()
        return

    # Notes section at bottom
    y -= 0.08 * inch
    section_label("Notes / Reflection", y)
    y -= 0.28 * inch
    lines_count = max(1, int((y - MARGIN - 0.12 * inch) / (0.225 * inch)))
    write_lines(y, lines_count, colors["line"], spacing=0.225)

    c.showPage()


def weekly_review_page(c, cfg, colors, week_num):
    draw_header_band(c, colors, f"Weekly Review — Week {week_num}")

    y = INNER_TOP - 0.65 * inch

    # Wins this week
    rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 6,
                 fill_color=colors["primary"])
    write_text(c, "Wins this week", INNER_X + 6, y + 4, "Helvetica-Bold", 10, colors["header_text"])
    y -= 0.38 * inch
    for _ in range(3):
        draw_line(c, INNER_X, y, PAGE_W - MARGIN, y, colors["line"], 0.5)
        y -= 0.22 * inch

    y -= 0.12 * inch

    # Challenges
    rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 6,
                 fill_color=colors["secondary"])
    write_text(c, "Challenges & what I learned", INNER_X + 6, y + 4, "Helvetica-Bold", 10, colors["header_text"])
    y -= 0.38 * inch
    for _ in range(3):
        draw_line(c, INNER_X, y, PAGE_W - MARGIN, y, colors["line"], 0.5)
        y -= 0.22 * inch

    y -= 0.12 * inch

    # Habit check-in
    rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 6,
                 fill_color=colors["accent"])
    write_text(c, "Habit check-in  (circle one for each)", INNER_X + 6, y + 4,
               "Helvetica-Bold", 10, colors["header_text"])
    y -= 0.38 * inch
    habit_labels = ["Exercise", "Sleep", "Nutrition", "Self-care", "Focus", "Connection"]
    for i, h in enumerate(habit_labels):
        col = i % 2
        row = i // 2
        bx = INNER_X + col * (INNER_W / 2)
        by = y - row * 0.32 * inch
        rounded_rect(c, bx + 2, by - 0.06 * inch, INNER_W / 2 - 8, 0.28 * inch, 5,
                     fill_color=colors["highlight"])
        write_text(c, f"{h}:  Great  Good  OK  Tough", bx + 8, by + 3, "Helvetica", 8.5, colors["text"])
    y -= (len(habit_labels) // 2 + 1) * 0.32 * inch

    y -= 0.12 * inch

    # Intention for next week
    remaining = y - MARGIN - 0.25 * inch
    if remaining > 0.6 * inch:
        rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 6,
                     fill_color=colors["primary"])
        write_text(c, "My intention for next week", INNER_X + 6, y + 4,
                   "Helvetica-Bold", 10, colors["header_text"])
        y -= 0.38 * inch
        lines_count = max(1, int(remaining / (0.22 * inch)) - 2)
        for _ in range(min(lines_count, 4)):
            draw_line(c, INNER_X, y, PAGE_W - MARGIN, y, colors["line"], 0.5)
            y -= 0.22 * inch

    c.showPage()


def sobriety_daily_page(c, cfg, colors, day_num):
    """BMP-002: Sobriety & Recovery daily page layout."""
    draw_header_band(c, colors, "My Recovery Planner", page_number=day_num)

    y = INNER_TOP - 0.65 * inch

    # Date + Craving/Urge level row
    rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.32 * inch, 6,
                 fill_color=colors["secondary"])
    write_text(c, "Date: _______________", INNER_X + 6, y + 4, "Helvetica", 9, colors["text"])
    write_text(c, "Urge: None  Mild  Moderate  Strong  Intense",
               INNER_X + 2.1 * inch, y + 4, "Helvetica", 8.5, colors["text"])
    y -= 0.42 * inch

    def section_label(label, sy):
        rounded_rect(c, INNER_X, sy, 1.5 * inch, 0.22 * inch, 4, fill_color=colors["accent"])
        write_text(c, label, INNER_X + 5, sy + 5, "Helvetica-Bold", 8, colors["header_text"])

    def write_lines(sy, count, spacing=0.235):
        for i in range(count):
            draw_line(c, INNER_X, sy - i * (spacing * inch),
                      PAGE_W - MARGIN, sy - i * (spacing * inch), colors["line"], 0.4)
        return sy - count * (spacing * inch) - 0.05 * inch

    # Today's Focus
    section_label("Today's Focus", y)
    y -= 0.27 * inch
    draw_line(c, INNER_X, y, PAGE_W - MARGIN, y, colors["line"], 0.4)
    y -= 0.30 * inch

    # Top 3 Priorities
    section_label("Top 3 Priorities", y)
    y -= 0.27 * inch
    y = write_lines(y, 3, spacing=0.235)

    # Time blocks (6 AM–9 PM)
    y -= 0.04 * inch
    section_label("Schedule", y)
    y -= 0.27 * inch
    times = ["6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM",
             "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM"]
    time_col_w = 0.55 * inch
    row_h_t = 0.175 * inch
    for i, t in enumerate(times):
        ry = y - i * row_h_t
        if ry < MARGIN + 1.15 * inch:
            break
        if i % 2 == 0:
            c.saveState()
            c.setFillColor(colors["secondary"])
            c.rect(INNER_X, ry - row_h_t + 3, INNER_W, row_h_t - 1, fill=1, stroke=0)
            c.restoreState()
        write_text(c, t, INNER_X + 2, ry - row_h_t + 5, "Helvetica", 7, colors["text"])
        draw_line(c, INNER_X + time_col_w, ry - row_h_t + 3,
                  PAGE_W - MARGIN, ry - row_h_t + 3, colors["line"], 0.3)
    y -= (min(len(times), 16) + 1) * row_h_t

    # Check-in row
    if y > MARGIN + 0.85 * inch:
        rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 5,
                     fill_color=colors["primary"])
        write_text(c, "✓ Meeting attended   ✓ Sponsor/support call   ✓ Water 8 cups   ✓ Sleep 7+ hrs",
                   INNER_X + 5, y + 4, "Helvetica", 8, colors["text"])
        y -= 0.38 * inch

    # Gratitude line
    if y > MARGIN + 0.55 * inch:
        write_text(c, "Grateful for:", INNER_X, y, "Helvetica-Bold", 9, colors["header_text"])
        draw_line(c, INNER_X + 0.85 * inch, y, PAGE_W - MARGIN, y, colors["line"], 0.4)
        y -= 0.32 * inch

    # Notes
    if y > MARGIN + 0.3 * inch:
        section_label("Notes", y)
        y -= 0.27 * inch
        lines_count = max(1, int((y - MARGIN - 0.1 * inch) / (0.225 * inch)))
        write_lines(y, lines_count, spacing=0.225)

    c.showPage()


def milestone_review_page(c, cfg, colors, milestone_days):
    """BMP-002: Sobriety milestone review page (at Day 7, 30, 60, 90)."""
    label = f"{milestone_days}-Day Milestone"
    draw_header_band(c, colors, label)

    y = INNER_TOP - 0.65 * inch

    # Milestone banner
    rounded_rect(c, INNER_X, y - 0.06 * inch, INNER_W, 0.42 * inch, 8,
                 fill_color=colors["accent"])
    centered_text(c, f"★  {milestone_days} Days — You're Doing This  ★",
                  y + 7, "Helvetica-Bold", 12, colors["header_text"])
    y -= 0.60 * inch

    # Days sober line
    write_text(c, "Days sober so far:", INNER_X, y, "Helvetica-Bold", 10, colors["header_text"])
    draw_line(c, INNER_X + 1.65 * inch, y, PAGE_W - MARGIN, y, colors["line"], 0.5)
    y -= 0.38 * inch

    def section_block(title, lines, block_color):
        nonlocal y
        rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 6,
                     fill_color=block_color)
        write_text(c, title, INNER_X + 6, y + 4, "Helvetica-Bold", 10, colors["header_text"])
        y -= 0.38 * inch
        for _ in range(lines):
            draw_line(c, INNER_X, y, PAGE_W - MARGIN, y, colors["line"], 0.5)
            y -= 0.235 * inch
        y -= 0.10 * inch

    section_block("What helped me this stretch?", 3, colors["secondary"])
    section_block("What was hardest?", 3, colors["primary"])
    section_block("One thing I'm proud of", 2, colors["highlight"])

    # Note to future self
    remaining = y - MARGIN - 0.25 * inch
    if remaining > 0.5 * inch:
        rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 6,
                     fill_color=colors["accent"])
        write_text(c, "Note to future self", INNER_X + 6, y + 4,
                   "Helvetica-Bold", 10, colors["header_text"])
        y -= 0.38 * inch
        lines_count = max(1, int(remaining / (0.235 * inch)) - 2)
        for _ in range(min(lines_count, 5)):
            draw_line(c, INNER_X, y, PAGE_W - MARGIN, y, colors["line"], 0.5)
            y -= 0.235 * inch

    c.showPage()


def chronic_pain_daily_page(c, cfg, colors, day_num):
    """BMP-003: Chronic Pain & Fatigue daily page layout."""
    draw_header_band(c, colors, "My Daily Tracker", page_number=day_num)

    y = INNER_TOP - 0.65 * inch

    # Date + Pain level row
    rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.32 * inch, 6,
                 fill_color=colors["secondary"])
    write_text(c, "Date: _______________", INNER_X + 6, y + 4, "Helvetica", 9, colors["text"])
    write_text(c, "Pain: 1  2  3  4  5  6  7  8  9  10",
               INNER_X + 2.1 * inch, y + 4, "Helvetica", 8.5, colors["text"])
    y -= 0.42 * inch

    # Energy / Spoon level
    rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 5,
                 fill_color=colors["highlight"])
    write_text(c, "Energy / Spoon Level:   Full    Good    Low    Empty",
               INNER_X + 6, y + 4, "Helvetica", 9, colors["text"])
    y -= 0.40 * inch

    def section_label(label, sy):
        rounded_rect(c, INNER_X, sy, 1.6 * inch, 0.22 * inch, 4, fill_color=colors["accent"])
        write_text(c, label, INNER_X + 5, sy + 5, "Helvetica-Bold", 8, colors["header_text"])

    def write_lines(sy, count, spacing=0.235):
        for i in range(count):
            draw_line(c, INNER_X, sy - i * (spacing * inch),
                      PAGE_W - MARGIN, sy - i * (spacing * inch), colors["line"], 0.4)
        return sy - count * (spacing * inch) - 0.05 * inch

    # Top 3 Gentle Goals
    section_label("Top 3 Gentle Goals", y)
    y -= 0.27 * inch
    y = write_lines(y, 3, spacing=0.235)

    # Energy Map time blocks (framed as high/low energy windows)
    y -= 0.04 * inch
    section_label("Energy Map", y)
    write_text(c, "(H = High  /  L = Low)", PAGE_W - MARGIN - 1.25 * inch, y + 5,
               "Helvetica", 7.5, colors["text"])
    y -= 0.27 * inch
    times = ["6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM",
             "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM"]
    time_col_w = 0.55 * inch
    row_h_t = 0.175 * inch
    for i, t in enumerate(times):
        ry = y - i * row_h_t
        if ry < MARGIN + 1.05 * inch:
            break
        if i % 2 == 0:
            c.saveState()
            c.setFillColor(colors["secondary"])
            c.rect(INNER_X, ry - row_h_t + 3, INNER_W, row_h_t - 1, fill=1, stroke=0)
            c.restoreState()
        write_text(c, t, INNER_X + 2, ry - row_h_t + 5, "Helvetica", 7, colors["text"])
        draw_line(c, INNER_X + time_col_w, ry - row_h_t + 3,
                  PAGE_W - MARGIN, ry - row_h_t + 3, colors["line"], 0.3)
    y -= (min(len(times), 16) + 1) * row_h_t

    # Check-in row
    if y > MARGIN + 0.85 * inch:
        rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 5,
                     fill_color=colors["primary"])
        write_text(c, "✓ Medication taken   ✓ Water 8 cups   ✓ Rest/pacing break   ✓ Sleep quality",
                   INNER_X + 5, y + 4, "Helvetica", 8, colors["text"])
        y -= 0.38 * inch

    # Symptom flare note
    if y > MARGIN + 0.55 * inch:
        write_text(c, "Flare note:", INNER_X, y, "Helvetica-Bold", 9, colors["header_text"])
        draw_line(c, INNER_X + 0.82 * inch, y, PAGE_W - MARGIN, y, colors["line"], 0.4)
        y -= 0.32 * inch

    # Notes
    if y > MARGIN + 0.3 * inch:
        section_label("Notes", y)
        y -= 0.27 * inch
        lines_count = max(1, int((y - MARGIN - 0.1 * inch) / (0.225 * inch)))
        write_lines(y, lines_count, spacing=0.225)

    c.showPage()


def chronic_pain_weekly_review_page(c, cfg, colors, week_num):
    """BMP-003: low-stimulation weekly review focused on pacing and symptoms."""
    draw_header_band(c, colors, f"Weekly Reflection — Week {week_num}")

    y = INNER_TOP - 0.65 * inch

    def section_block(title, lines, block_color):
        nonlocal y
        rounded_rect(c, INNER_X, y - 0.04 * inch, INNER_W, 0.28 * inch, 6,
                     fill_color=block_color)
        write_text(c, title, INNER_X + 6, y + 4, "Helvetica-Bold", 10, colors["header_text"])
        y -= 0.38 * inch
        for _ in range(lines):
            draw_line(c, INNER_X, y, PAGE_W - MARGIN, y, colors["line"], 0.5)
            y -= 0.22 * inch
        y -= 0.12 * inch

    section_block("What went well this week?", 3, colors["secondary"])
    section_block("What was challenging?", 3, colors["primary"])
    section_block("What triggered flares, if anything?", 2, colors["highlight"])
    section_block("What helped me manage symptoms?", 2, colors["accent"])

    remaining = y - MARGIN - 0.25 * inch
    if remaining > 0.5 * inch:
        section_block("One pacing adjustment for next week", 2, colors["secondary"])

    remaining = y - MARGIN - 0.25 * inch
    if remaining > 0.5 * inch:
        section_block("Wins to celebrate", 2, colors["accent"])

    c.showPage()


def blank_notes_page(c, cfg, colors, label="Notes"):
    draw_header_band(c, colors, label)
    y = INNER_TOP - 0.65 * inch
    line_spacing = 0.235 * inch
    count = int((y - MARGIN - 0.15 * inch) / line_spacing)
    for i in range(count):
        ly = y - i * line_spacing
        draw_line(c, INNER_X, ly, PAGE_W - MARGIN, ly, colors["line"], 0.4)
    c.showPage()


# ── Page count helper (for pre-validation) ────────────────────────────────────
SOBRIETY_MILESTONES = [7, 30, 60, 90]

def compute_page_count(cfg):
    day_count = int(cfg.get("dayCount", 60))
    include_habit = cfg.get("includeHabitTracker", True)
    include_weekly = cfg.get("includeWeeklyReview", True)
    book_type = cfg.get("bookType", "")

    pages = 2  # title + intro
    if include_habit:
        months = max(1, math.ceil(day_count / 30))
        pages += months
    pages += day_count  # daily pages
    if book_type == "sobriety":
        # Milestone reviews at days 7, 30, 60, 90 (instead of every 7 days)
        pages += sum(1 for m in SOBRIETY_MILESTONES if m <= day_count)
    elif include_weekly:
        pages += day_count // 7  # weekly reviews
    # KDP minimum: 72 for full color, 24 for B&W
    interior_type = cfg.get("interiorType", "full_color")
    minimum = 72 if interior_type == "full_color" else 24
    while pages < minimum:
        pages += 1  # will add blank notes
    return pages


# ── Main generator ────────────────────────────────────────────────────────────
def generate(cfg, output_path):
    palette_key = cfg.get("colorPalette", "lavender_mint")
    colors = PALETTES.get(palette_key, PALETTES["lavender_mint"])

    day_count = int(cfg.get("dayCount", 60))
    include_habit = cfg.get("includeHabitTracker", True)
    include_weekly = cfg.get("includeWeeklyReview", True)
    interior_type = cfg.get("interiorType", "full_color")
    book_type = cfg.get("bookType", "")
    minimum = 72 if interior_type == "full_color" else 24

    c = rl_canvas.Canvas(output_path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle(cfg.get("topic", "Daily Planner"))
    c.setAuthor(cfg.get("authorName", "Bright Mindful Pages"))

    pages_generated = 0

    # 1. Title page
    title_page(c, cfg, colors)
    pages_generated += 1

    # 2. Intro page
    intro_page(c, cfg, colors)
    pages_generated += 1

    # 3. Habit tracker page(s)
    if include_habit:
        months = max(1, math.ceil(day_count / 30))
        for m in range(months):
            habit_tracker_page(c, cfg, colors, f"Month {m + 1}")
            pages_generated += 1

    # 4. Daily pages + reviews (dispatches by book_type)
    if book_type == "sobriety":
        # Sobriety: milestone review pages at days 7, 30, 60, 90
        for day in range(1, day_count + 1):
            sobriety_daily_page(c, cfg, colors, day)
            pages_generated += 1
            if day in SOBRIETY_MILESTONES:
                milestone_review_page(c, cfg, colors, day)
                pages_generated += 1
    elif book_type == "chronic_pain":
        # Chronic pain: custom daily page + standard weekly reviews (reframed language handled in page)
        for day in range(1, day_count + 1):
            chronic_pain_daily_page(c, cfg, colors, day)
            pages_generated += 1
            if include_weekly and day % 7 == 0:
                week_num = day // 7
                chronic_pain_weekly_review_page(c, cfg, colors, week_num)
                pages_generated += 1
    else:
        # Default: standard ADHD/anxiety/gratitude layout
        for day in range(1, day_count + 1):
            daily_page(c, cfg, colors, day)
            pages_generated += 1
            if include_weekly and day % 7 == 0:
                week_num = day // 7
                weekly_review_page(c, cfg, colors, week_num)
                pages_generated += 1

    # 5. Pad to minimum with blank notes pages
    note_labels = ["Bonus Notes", "Extra Notes", "Free Writing", "Reflections",
                   "Gratitude Log", "Ideas & Inspiration"]
    note_idx = 0
    while pages_generated < minimum:
        label = note_labels[note_idx % len(note_labels)]
        blank_notes_page(c, cfg, colors, label)
        pages_generated += 1
        note_idx += 1

    c.save()
    return pages_generated


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: generate_book.py '<json_cfg>' <output_path>"}))
        sys.exit(1)
    cfg = json.loads(sys.argv[1])
    output_path = sys.argv[2]
    try:
        pages = generate(cfg, output_path)
        print(json.dumps({"success": True, "pages": pages, "outputPath": output_path}))
    except Exception as e:
        import traceback
        print(json.dumps({"error": str(e), "trace": traceback.format_exc()}))
        sys.exit(1)
