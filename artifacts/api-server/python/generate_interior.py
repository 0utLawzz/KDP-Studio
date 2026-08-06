#!/usr/bin/env python3
"""
KDP Interior PDF Generator — Bright Mindful Pages
Generates KDP-compliant book interiors (planners, trackers).
MARGIN: 0.4in on all sides (fixed — never change).
"""

import sys
import os
import json
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

# ── Constants ─────────────────────────────────────────────────────────────────
MARGIN = 0.4 * inch   # KDP spec: 0.4in on all sides — FIXED, do not change
MIN_PAGES_COLOR = 72  # KDP minimum for full-color interior
MIN_PAGES_BW = 24     # KDP minimum for B&W interior

TRIM_SIZES = {
    "6x9": (6 * inch, 9 * inch),
    "5x8": (5 * inch, 8 * inch),
    "8.5x11": (8.5 * inch, 11 * inch),
}

# ── Color Palettes ────────────────────────────────────────────────────────────
PALETTES = {
    "lavender_mint": {
        "primary": colors.HexColor("#C9B8E8"),
        "secondary": colors.HexColor("#A8D8C8"),
        "accent": colors.HexColor("#E8D5F0"),
        "highlight": colors.HexColor("#F5F0FF"),
        "text": colors.HexColor("#4A4A6A"),
        "header_text": colors.white,
    },
    "sage_teal": {
        "primary": colors.HexColor("#7BA08C"),
        "secondary": colors.HexColor("#5B8FA8"),
        "accent": colors.HexColor("#A8C5B5"),
        "highlight": colors.HexColor("#F0F7F4"),
        "text": colors.HexColor("#2D4A3E"),
        "header_text": colors.white,
    },
    "rose_gold": {
        "primary": colors.HexColor("#C4847A"),
        "secondary": colors.HexColor("#D4A8A0"),
        "accent": colors.HexColor("#F0D0CC"),
        "highlight": colors.HexColor("#FDF5F4"),
        "text": colors.HexColor("#5A2D2D"),
        "header_text": colors.white,
    },
    "ocean_breeze": {
        "primary": colors.HexColor("#6B9DC2"),
        "secondary": colors.HexColor("#89C4D4"),
        "accent": colors.HexColor("#B8DDE8"),
        "highlight": colors.HexColor("#F0F8FF"),
        "text": colors.HexColor("#1A3D5C"),
        "header_text": colors.white,
    },
    "sunset_peach": {
        "primary": colors.HexColor("#E8956D"),
        "secondary": colors.HexColor("#F4B896"),
        "accent": colors.HexColor("#FAD5B8"),
        "highlight": colors.HexColor("#FFF5EE"),
        "text": colors.HexColor("#6B3020"),
        "header_text": colors.white,
    },
    "forest_fern": {
        "primary": colors.HexColor("#5B8C5A"),
        "secondary": colors.HexColor("#7BAF7A"),
        "accent": colors.HexColor("#A8CCA8"),
        "highlight": colors.HexColor("#F0F7F0"),
        "text": colors.HexColor("#1F3D1F"),
        "header_text": colors.white,
    },
    "dusty_plum": {
        "primary": colors.HexColor("#8B6B8B"),
        "secondary": colors.HexColor("#A88BA8"),
        "accent": colors.HexColor("#C8A8C8"),
        "highlight": colors.HexColor("#F5EEF5"),
        "text": colors.HexColor("#3D1F3D"),
        "header_text": colors.white,
    },
    "golden_hour": {
        "primary": colors.HexColor("#D4A843"),
        "secondary": colors.HexColor("#E8C878"),
        "accent": colors.HexColor("#F5E0A0"),
        "highlight": colors.HexColor("#FFFBF0"),
        "text": colors.HexColor("#5A3C00"),
        "header_text": colors.white,
    },
    "arctic_blue": {
        "primary": colors.HexColor("#7098B8"),
        "secondary": colors.HexColor("#90B8D8"),
        "accent": colors.HexColor("#B8D5E8"),
        "highlight": colors.HexColor("#F0F5FF"),
        "text": colors.HexColor("#1A2D4A"),
        "header_text": colors.white,
    },
    "terracotta": {
        "primary": colors.HexColor("#C4714A"),
        "secondary": colors.HexColor("#D89070"),
        "accent": colors.HexColor("#EBB898"),
        "highlight": colors.HexColor("#FDF2EC"),
        "text": colors.HexColor("#5C2010"),
        "header_text": colors.white,
    },
    "mint_chocolate": {
        "primary": colors.HexColor("#6BAA8C"),
        "secondary": colors.HexColor("#8B5A3C"),
        "accent": colors.HexColor("#A8D5C0"),
        "highlight": colors.HexColor("#F0FFF8"),
        "text": colors.HexColor("#1C3D2D"),
        "header_text": colors.white,
    },
}


def get_palette(key):
    return PALETTES.get(key, PALETTES["lavender_mint"])


def calculate_page_count(book_type, day_count, include_habit_tracker=True, include_weekly_review=True):
    """Calculate expected page count for a book configuration."""
    pages = 4  # front matter: title, copyright, intro (2 pages each)
    if book_type == "sobriety":
        pages += day_count * 2  # daily page + mood tracker per day
        pages += day_count // 7  # weekly milestones
    else:
        pages += day_count
        if include_habit_tracker:
            pages += (day_count + 6) // 7
        if include_weekly_review:
            pages += (day_count + 6) // 7
    pages += 2  # back matter
    return pages


class DailyPlannerCanvas:
    """Draws a single daily planner page onto a canvas."""

    def __init__(self, c, palette, page_width, page_height, day_num, date_label=None):
        self.c = c
        self.p = palette
        self.w = page_width
        self.h = page_height
        self.day = day_num
        self.date_label = date_label or f"Day {day_num}"
        self.margin = MARGIN

    def draw(self):
        c = self.c
        p = self.p
        w, h, m = self.w, self.h, self.margin

        # Header band
        c.setFillColor(p["primary"])
        c.rect(0, h - 0.7 * inch, w, 0.7 * inch, fill=1, stroke=0)

        # Day number
        c.setFillColor(p["header_text"])
        c.setFont("Helvetica-Bold", 16)
        c.drawString(m, h - 0.5 * inch, self.date_label)

        # Morning intentions section
        y = h - 1.0 * inch
        c.setFillColor(p["text"])
        c.setFont("Helvetica-Bold", 9)
        c.drawString(m, y, "Morning Intentions")
        y -= 0.05 * inch

        c.setStrokeColor(p["secondary"])
        c.setLineWidth(0.5)
        for _ in range(3):
            y -= 0.22 * inch
            c.line(m, y, w - m, y)

        # Top priorities
        y -= 0.25 * inch
        c.setFillColor(p["primary"])
        c.roundRect(m, y - 0.18 * inch, w - 2 * m, 0.22 * inch, 4, fill=1, stroke=0)
        c.setFillColor(p["header_text"])
        c.setFont("Helvetica-Bold", 8)
        c.drawString(m + 0.08 * inch, y - 0.06 * inch, "TOP 3 PRIORITIES")
        y -= 0.18 * inch

        c.setStrokeColor(p["accent"])
        c.setLineWidth(0.8)
        for i in range(3):
            y -= 0.22 * inch
            c.setFillColor(p["accent"])
            c.circle(m + 0.08 * inch, y + 0.07 * inch, 0.06 * inch, fill=1, stroke=0)
            c.setStrokeColor(p["secondary"])
            c.setLineWidth(0.5)
            c.line(m + 0.22 * inch, y, w - m, y)

        # Time blocks
        y -= 0.3 * inch
        c.setFillColor(p["text"])
        c.setFont("Helvetica-Bold", 9)
        c.drawString(m, y, "Schedule")
        y -= 0.05 * inch

        hours = ["6am", "7am", "8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm"]
        block_h = 0.18 * inch
        label_w = 0.4 * inch
        for i, hour in enumerate(hours):
            if y - block_h < m:
                break
            # Alternating background
            if i % 2 == 0:
                c.setFillColor(p["highlight"])
                c.rect(m, y - block_h, w - 2 * m, block_h, fill=1, stroke=0)
            c.setFillColor(p["text"])
            c.setFont("Helvetica", 7)
            c.drawString(m + 0.02 * inch, y - 0.13 * inch, hour)
            c.setStrokeColor(p["accent"])
            c.setLineWidth(0.3)
            c.line(m + label_w, y - block_h / 2, w - m, y - block_h / 2)
            y -= block_h

        # Evening reflection
        if y > m + 0.8 * inch:
            y -= 0.15 * inch
            c.setFillColor(p["secondary"])
            c.roundRect(m, y - 0.18 * inch, w - 2 * m, 0.22 * inch, 4, fill=1, stroke=0)
            c.setFillColor(p["header_text"])
            c.setFont("Helvetica-Bold", 8)
            c.drawString(m + 0.08 * inch, y - 0.06 * inch, "EVENING REFLECTION")
            y -= 0.18 * inch
            c.setStrokeColor(p["secondary"])
            c.setLineWidth(0.5)
            for _ in range(2):
                y -= 0.22 * inch
                if y > m:
                    c.line(m, y, w - m, y)

        # Gratitude footer
        if y > m + 0.4 * inch:
            y -= 0.2 * inch
            c.setFillColor(p["accent"])
            c.rect(m, m, w - 2 * m, 0.24 * inch, fill=1, stroke=0)
            c.setFillColor(p["text"])
            c.setFont("Helvetica-Oblique", 7)
            c.drawString(m + 0.06 * inch, m + 0.07 * inch, "Today I'm grateful for: ________________________")


class SobrietyDailyCanvas:
    """Draws a sobriety daily tracker page."""

    def __init__(self, c, palette, page_width, page_height, day_num):
        self.c = c
        self.p = palette
        self.w = page_width
        self.h = page_height
        self.day = day_num
        self.margin = MARGIN

    def draw(self):
        c = self.c
        p = self.p
        w, h, m = self.w, self.h, self.margin

        # Header
        c.setFillColor(p["primary"])
        c.rect(0, h - 0.7 * inch, w, 0.7 * inch, fill=1, stroke=0)
        c.setFillColor(p["header_text"])
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(w / 2, h - 0.48 * inch, f"Day {self.day}")

        y = h - 1.0 * inch

        # Milestone badge
        milestone_text = None
        if self.day == 1: milestone_text = "First Step"
        elif self.day == 7: milestone_text = "One Week Strong"
        elif self.day == 30: milestone_text = "30 Days — Keep Going"
        elif self.day == 60: milestone_text = "60 Days — You're Doing It"
        elif self.day == 90: milestone_text = "90 Days — Life is Changing"

        if milestone_text:
            c.setFillColor(p["accent"])
            c.roundRect(m, y - 0.22 * inch, w - 2 * m, 0.26 * inch, 6, fill=1, stroke=0)
            c.setFillColor(p["text"])
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(w / 2, y - 0.08 * inch, f"Milestone: {milestone_text}")
            y -= 0.32 * inch

        # Mood tracker
        y -= 0.1 * inch
        c.setFillColor(p["text"])
        c.setFont("Helvetica-Bold", 9)
        c.drawString(m, y, "How am I feeling today?")
        y -= 0.28 * inch
        moods = ["Struggling", "Okay", "Good", "Strong", "Grateful"]
        mood_w = (w - 2 * m) / len(moods)
        for i, mood in enumerate(moods):
            x = m + i * mood_w + mood_w / 2
            c.setStrokeColor(p["primary"])
            c.setFillColor(p["highlight"])
            c.setLineWidth(1)
            c.circle(x, y, 0.18 * inch, fill=1, stroke=1)
            c.setFillColor(p["text"])
            c.setFont("Helvetica", 6)
            c.drawCentredString(x, y - 0.28 * inch, mood)
        y -= 0.45 * inch

        # Urge tracker
        c.setFillColor(p["text"])
        c.setFont("Helvetica-Bold", 9)
        c.drawString(m, y, "Urge intensity (circle one)")
        y -= 0.28 * inch
        for i in range(1, 11):
            x = m + (i - 1) * (w - 2 * m) / 10 + (w - 2 * m) / 20
            c.setStrokeColor(p["secondary"])
            c.setFillColor(p["highlight"])
            c.setLineWidth(0.8)
            c.circle(x, y, 0.12 * inch, fill=1, stroke=1)
            c.setFillColor(p["text"])
            c.setFont("Helvetica", 7)
            c.drawCentredString(x, y - 0.04 * inch, str(i))
        y -= 0.35 * inch

        # Sections
        sections = [
            ("What helped me today?", 3),
            ("What I'm grateful for:", 2),
            ("Tomorrow's intention:", 2),
            ("Notes / reflections:", 4),
        ]
        for label, line_count in sections:
            if y - (line_count + 1) * 0.22 * inch < m:
                break
            c.setFillColor(p["text"])
            c.setFont("Helvetica-Bold", 9)
            c.drawString(m, y, label)
            y -= 0.06 * inch
            c.setStrokeColor(p["secondary"])
            c.setLineWidth(0.5)
            for _ in range(line_count):
                y -= 0.22 * inch
                c.line(m, y, w - m, y)
            y -= 0.15 * inch


def generate_interior(args, output_path):
    palette_key = args.color_palette or "lavender_mint"
    p = get_palette(palette_key)
    page_size = TRIM_SIZES.get(args.trim_size or "6x9", TRIM_SIZES["6x9"])
    pw, ph = page_size
    book_type = args.book_type or "default"
    day_count = int(args.day_count or 60)
    include_habit = args.include_habit_tracker
    include_weekly = args.include_weekly_review

    c = canvas.Canvas(output_path, pagesize=page_size)

    page_num = 0

    def _new_page():
        nonlocal page_num
        if page_num > 0:
            c.showPage()
        page_num += 1

    # ── Title page ────────────────────────────────────────────────────────────
    _new_page()
    c.setFillColor(p["primary"])
    c.rect(0, ph * 0.6, pw, ph * 0.4, fill=1, stroke=0)
    c.setFillColor(p["accent"])
    c.rect(0, ph * 0.58, pw, ph * 0.02, fill=1, stroke=0)
    c.setFillColor(p["header_text"])
    c.setFont("Helvetica-Bold", 22)
    title_text = args.title or "My Daily Planner"
    c.drawCentredString(pw / 2, ph * 0.78, title_text)
    c.setFont("Helvetica", 12)
    c.drawCentredString(pw / 2, ph * 0.68, f"{day_count}-Day Journey")
    c.setFillColor(p["text"])
    c.setFont("Helvetica", 10)
    c.drawCentredString(pw / 2, ph * 0.45, args.author_name or "Bright Mindful Pages")

    # ── Copyright page ────────────────────────────────────────────────────────
    _new_page()
    c.setFillColor(p["text"])
    c.setFont("Helvetica", 8)
    year = 2025
    copyright_lines = [
        f"© {year} {args.author_name or 'Bright Mindful Pages'}",
        "All rights reserved. No part of this publication may be reproduced",
        "or transmitted in any form without written permission.",
        "",
        "Published independently.",
        "Printed in the United States of America.",
    ]
    y = ph / 2
    for line in copyright_lines:
        c.drawCentredString(pw / 2, y, line)
        y -= 0.2 * inch

    # ── Introduction page ─────────────────────────────────────────────────────
    _new_page()
    c.setFillColor(p["primary"])
    c.rect(0, ph - 1.0 * inch, pw, 1.0 * inch, fill=1, stroke=0)
    c.setFillColor(p["header_text"])
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(pw / 2, ph - 0.65 * inch, "How to Use This Planner")
    c.setFillColor(p["text"])
    c.setFont("Helvetica", 9)
    intro_text = (
        "Welcome to your journey. Each day, take a few minutes in the morning to set "
        "your intentions and in the evening to reflect on your progress. Small, "
        "consistent actions create lasting change. You've got this."
    )
    y = ph - 1.3 * inch
    words = intro_text.split()
    line = ""
    for word in words:
        test = line + (" " if line else "") + word
        if c.stringWidth(test, "Helvetica", 9) > pw - 2 * MARGIN:
            c.drawString(MARGIN, y, line)
            y -= 0.18 * inch
            line = word
        else:
            line = test
    if line:
        c.drawString(MARGIN, y, line)

    # ── Blank verso ────────────────────────────────────────────────────────────
    _new_page()

    # ── Daily pages ────────────────────────────────────────────────────────────
    for day in range(1, day_count + 1):
        _new_page()
        if book_type == "sobriety":
            drawer = SobrietyDailyCanvas(c, p, pw, ph, day)
        else:
            drawer = DailyPlannerCanvas(c, p, pw, ph, day)
        drawer.draw()

        # Sobriety gets a second page (mood/reflection page)
        if book_type == "sobriety":
            _new_page()
            c.setFillColor(p["secondary"])
            c.rect(0, ph - 0.4 * inch, pw, 0.4 * inch, fill=1, stroke=0)
            c.setFillColor(p["header_text"])
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(pw / 2, ph - 0.27 * inch, f"Day {day} — Deeper Reflection")
            y = ph - 0.7 * inch
            sections = ["What emotions came up today?", "Coping strategies I used:", "What I want to remember:", "Message to my future self:"]
            for section in sections:
                if y - 4 * 0.22 * inch < MARGIN:
                    break
                c.setFillColor(p["text"])
                c.setFont("Helvetica-Bold", 9)
                c.drawString(MARGIN, y, section)
                y -= 0.06 * inch
                c.setStrokeColor(p["secondary"])
                c.setLineWidth(0.5)
                for _ in range(3):
                    y -= 0.22 * inch
                    c.line(MARGIN, y, pw - MARGIN, y)
                y -= 0.2 * inch

        # Weekly habit tracker
        if book_type != "sobriety" and include_habit and day % 7 == 0:
            week_num = day // 7
            _new_page()
            c.setFillColor(p["primary"])
            c.rect(0, ph - 0.7 * inch, pw, 0.7 * inch, fill=1, stroke=0)
            c.setFillColor(p["header_text"])
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(pw / 2, ph - 0.47 * inch, f"Week {week_num} — Habit Tracker")
            y = ph - 1.1 * inch
            days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            habits = ["Morning routine", "Exercise", "Water (8 cups)", "Meditation", "Reading", "Journaling", "Sleep 7hrs+"]
            cell_w = (pw - 2 * MARGIN - 1.2 * inch) / 7
            # Header row
            c.setFillColor(p["secondary"])
            c.roundRect(MARGIN + 1.2 * inch, y - 0.22 * inch, cell_w * 7, 0.25 * inch, 3, fill=1, stroke=0)
            c.setFillColor(p["header_text"])
            c.setFont("Helvetica-Bold", 8)
            for i, d in enumerate(days_of_week):
                c.drawCentredString(MARGIN + 1.2 * inch + (i + 0.5) * cell_w, y - 0.08 * inch, d)
            y -= 0.25 * inch
            for j, habit in enumerate(habits):
                if y - 0.28 * inch < MARGIN:
                    break
                bg = p["highlight"] if j % 2 == 0 else colors.white
                c.setFillColor(bg)
                c.rect(MARGIN, y - 0.25 * inch, pw - 2 * MARGIN, 0.25 * inch, fill=1, stroke=0)
                c.setFillColor(p["text"])
                c.setFont("Helvetica", 8)
                c.drawString(MARGIN + 0.05 * inch, y - 0.14 * inch, habit)
                for k in range(7):
                    cx = MARGIN + 1.2 * inch + (k + 0.5) * cell_w
                    cy = y - 0.125 * inch
                    c.setStrokeColor(p["primary"])
                    c.setFillColor(colors.white)
                    c.setLineWidth(0.8)
                    c.rect(cx - 0.09 * inch, cy - 0.09 * inch, 0.18 * inch, 0.18 * inch, fill=1, stroke=1)
                y -= 0.25 * inch

        # Weekly review
        if book_type != "sobriety" and include_weekly and day % 7 == 0:
            week_num = day // 7
            _new_page()
            c.setFillColor(p["secondary"])
            c.rect(0, ph - 0.7 * inch, pw, 0.7 * inch, fill=1, stroke=0)
            c.setFillColor(p["header_text"])
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(pw / 2, ph - 0.47 * inch, f"Week {week_num} — Weekly Review")
            y = ph - 1.0 * inch
            prompts = [
                ("This week's biggest win:", 2),
                ("What challenged me most?", 2),
                ("What I want to improve next week:", 3),
                ("Gratitude — 3 things I'm thankful for:", 3),
                ("Next week's main focus:", 2),
            ]
            for prompt, lines in prompts:
                if y - (lines + 1) * 0.22 * inch < MARGIN:
                    break
                c.setFillColor(p["text"])
                c.setFont("Helvetica-Bold", 9)
                c.drawString(MARGIN, y, prompt)
                y -= 0.06 * inch
                c.setStrokeColor(p["secondary"])
                c.setLineWidth(0.5)
                for _ in range(lines):
                    y -= 0.22 * inch
                    c.line(MARGIN, y, pw - MARGIN, y)
                y -= 0.18 * inch

    # Sobriety weekly milestones
    if book_type == "sobriety":
        for week in range(1, (day_count // 7) + 1):
            _new_page()
            c.setFillColor(p["accent"])
            c.rect(0, 0, pw, ph, fill=1, stroke=0)
            c.setFillColor(p["primary"])
            c.circle(pw / 2, ph / 2, 1.4 * inch, fill=1, stroke=0)
            c.setFillColor(p["header_text"])
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(pw / 2, ph / 2 + 0.2 * inch, f"{week * 7}")
            c.setFont("Helvetica", 12)
            c.drawCentredString(pw / 2, ph / 2 - 0.25 * inch, "DAYS")
            c.setFillColor(p["text"])
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(pw / 2, ph / 2 - 1.8 * inch, "You made it another week.")
            c.setFont("Helvetica", 9)
            c.drawCentredString(pw / 2, ph / 2 - 2.1 * inch, "Every single day counts.")

    # ── Back matter ────────────────────────────────────────────────────────────
    _new_page()
    c.setFillColor(p["primary"])
    c.rect(0, ph - 0.7 * inch, pw, 0.7 * inch, fill=1, stroke=0)
    c.setFillColor(p["header_text"])
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(pw / 2, ph - 0.47 * inch, "Notes")
    y = ph - 1.0 * inch
    c.setStrokeColor(p["secondary"])
    c.setLineWidth(0.5)
    while y > MARGIN + 0.22 * inch:
        c.line(MARGIN, y, pw - MARGIN, y)
        y -= 0.28 * inch

    _new_page()
    c.setFillColor(p["accent"])
    c.rect(0, 0, pw, ph, fill=1, stroke=0)
    c.setFillColor(p["text"])
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(pw / 2, ph / 2 + 0.3 * inch, "You did it.")
    c.setFont("Helvetica", 10)
    c.drawCentredString(pw / 2, ph / 2, f"{day_count} days of intentional living.")
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(pw / 2, ph / 2 - 0.4 * inch, args.author_name or "Bright Mindful Pages")

    c.save()
    return page_num


def main():
    parser = argparse.ArgumentParser(description="Generate KDP interior PDF")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--title", default="My Daily Planner")
    parser.add_argument("--author-name", default="Bright Mindful Pages")
    parser.add_argument("--book-type", default="default", choices=["default", "sobriety", "chronic_pain"])
    parser.add_argument("--color-palette", default="lavender_mint")
    parser.add_argument("--trim-size", default="6x9", choices=["6x9", "5x8", "8.5x11"])
    parser.add_argument("--day-count", type=int, default=60)
    parser.add_argument("--interior-type", default="full_color", choices=["full_color", "black_white"])
    parser.add_argument("--include-habit-tracker", action="store_true", default=True)
    parser.add_argument("--no-habit-tracker", dest="include_habit_tracker", action="store_false")
    parser.add_argument("--include-weekly-review", action="store_true", default=True)
    parser.add_argument("--no-weekly-review", dest="include_weekly_review", action="store_false")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    page_count = generate_interior(args, args.output)

    result = {
        "success": True,
        "page_count": page_count,
        "output": args.output,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
