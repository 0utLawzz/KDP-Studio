#!/usr/bin/env python3
"""Generate editable Canva/Affinity-friendly SVG/PDF template assets.

Usage: python3 generate_editable_template.py '<json_config>' <output_zip>
"""

from __future__ import annotations

import html
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas as rl_canvas


BLEED_IN = 0.125
SAFE_INSET_IN = 0.5
SPINE_MULTIPLIER = {
    "white": 0.002252,
    "cream": 0.0025,
    "standard_color": 0.002252,
    "premium_color": 0.002347,
}
TRIM_SIZES_IN = {
    "6x9": (6.0, 9.0),
    "5x8": (5.0, 8.0),
    "8.5x11": (8.5, 11.0),
}
PALETTES = {
    "lavender_mint": {
        "primary": "#E6D9F7",
        "secondary": "#D6F3E8",
        "accent": "#FBD6E3",
        "highlight": "#D9EEFB",
        "text": "#4A3F55",
        "header_text": "#6B5580",
        "dark": "#3D2F4A",
        "line": "#C4B8D4",
    },
    "ocean_peach": {
        "primary": "#D9EEFB",
        "secondary": "#FFE3D1",
        "accent": "#B8D8F0",
        "highlight": "#FFDFC4",
        "text": "#2D4A5E",
        "header_text": "#2D6080",
        "dark": "#1A3344",
        "line": "#A8C8E0",
    },
    "sky_pink": {
        "primary": "#FBD6E3",
        "secondary": "#D9EEFB",
        "accent": "#E6D9F7",
        "highlight": "#FFE3D1",
        "text": "#5C2D4E",
        "header_text": "#8B3060",
        "dark": "#3A1A30",
        "line": "#E0A0BC",
    },
    "forest_earth": {
        "primary": "#D8EAD4",
        "secondary": "#F5E6D0",
        "accent": "#B8D4C0",
        "highlight": "#EAD8C4",
        "text": "#2C3E28",
        "header_text": "#3A5C34",
        "dark": "#1E2A1A",
        "line": "#8EAA86",
    },
    "sage_teal": {
        "primary": "#C9DCC5",
        "secondary": "#BEE3DB",
        "accent": "#F0D3D8",
        "highlight": "#F2E4D0",
        "text": "#4A3F55",
        "header_text": "#3A6B50",
        "dark": "#2E5842",
        "line": "#9ABEA8",
    },
    "lavender_grey": {
        "primary": "#E6D9F7",
        "secondary": "#DCE3EA",
        "accent": "#D6F3E8",
        "highlight": "#FFE3D1",
        "text": "#4A3F55",
        "header_text": "#5A6A8A",
        "dark": "#46536E",
        "line": "#B0BEC5",
    },
    "cobalt_coral": {
        "primary": "#BFDBFE",
        "secondary": "#FDA4AF",
        "accent": "#FDE68A",
        "highlight": "#DBEAFE",
        "text": "#172554",
        "header_text": "#1D4ED8",
        "dark": "#1E3A8A",
        "line": "#93C5FD",
    },
    "sunshine_mint": {
        "primary": "#FEF08A",
        "secondary": "#A7F3D0",
        "accent": "#BAE6FD",
        "highlight": "#ECFCCB",
        "text": "#14532D",
        "header_text": "#166534",
        "dark": "#14532D",
        "line": "#86EFAC",
    },
    "berry_pop": {
        "primary": "#F9A8D4",
        "secondary": "#C4B5FD",
        "accent": "#FED7AA",
        "highlight": "#FCE7F3",
        "text": "#581C87",
        "header_text": "#9D174D",
        "dark": "#581C87",
        "line": "#D8B4FE",
    },
    "ocean_lime": {
        "primary": "#7DD3FC",
        "secondary": "#BEF264",
        "accent": "#99F6E4",
        "highlight": "#DBEAFE",
        "text": "#082F49",
        "header_text": "#0369A1",
        "dark": "#082F49",
        "line": "#67E8F9",
    },
    "tangerine_sky": {
        "primary": "#FDBA74",
        "secondary": "#7DD3FC",
        "accent": "#FEF3C7",
        "highlight": "#E0F2FE",
        "text": "#172554",
        "header_text": "#C2410C",
        "dark": "#172554",
        "line": "#93C5FD",
    },
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def safe_topic(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in cleaned.split("-") if part)[:40] or "daily-planner"


def dimensions(cfg: dict) -> dict:
    trim_w, trim_h = TRIM_SIZES_IN.get(cfg.get("trimSize", "6x9"), TRIM_SIZES_IN["6x9"])
    page_count = max(1, int(round(float(cfg.get("pageCount", 72)))))
    paper = cfg.get("paperType")
    if paper not in SPINE_MULTIPLIER:
        paper = "premium_color" if cfg.get("interiorType") == "full_color" else "white"
    spine = page_count * SPINE_MULTIPLIER[paper]
    return {
        "trim_w": trim_w,
        "trim_h": trim_h,
        "spine": spine,
        "full_w": BLEED_IN + trim_w + spine + trim_w + BLEED_IN,
        "full_h": BLEED_IN + trim_h + BLEED_IN,
        "page_count": page_count,
        "paper": paper,
    }


def svg_text(x: float, y: float, value: str, size: int, color: str, anchor: str = "middle", weight: str = "normal", editable_id: str = "") -> str:
    identifier = f' id="{esc(editable_id)}"' if editable_id else ""
    return (
        f'<text{identifier} data-editable="true" x="{x:.3f}" y="{y:.3f}" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}" '
        f'fill="{esc(color)}" text-anchor="{anchor}">{esc(value)}</text>'
    )


def svg_rect(x: float, y: float, width: float, height: float, fill: str, identifier: str = "", stroke: str = "none", dash: str = "") -> str:
    id_attr = f' id="{esc(identifier)}"' if identifier else ""
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect{id_attr} data-editable="true" x="{x:.3f}" y="{y:.3f}" width="{width:.3f}" height="{height:.3f}" fill="{esc(fill)}" stroke="{esc(stroke)}"{dash_attr}/>'


def cover_svg(cfg: dict, dims: dict, colors: dict) -> str:
    scale = 72
    width = dims["full_w"] * scale
    height = dims["full_h"] * scale
    bleed = BLEED_IN * scale
    trim_w = dims["trim_w"] * scale
    trim_h = dims["trim_h"] * scale
    spine = dims["spine"] * scale
    back_x = bleed
    spine_x = bleed + trim_w
    front_x = spine_x + spine
    safe = SAFE_INSET_IN * scale
    center_x = front_x + trim_w / 2
    topic = cfg.get("topic", "Daily Planner")
    subtitle = cfg.get("subtitle") or f"A thoughtful companion for {cfg.get('niche', 'your journey')}"
    author = cfg.get("authorName", "Bright Mindful Pages")
    audience = f"For {cfg.get('targetAudience', 'Adults')}"
    blurb = f"A practical, calming space to support your {cfg.get('niche', 'daily')} journey."
    spine_text = topic if dims["page_count"] >= 79 else "Spine text only at 79+ pages"
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{dims["full_w"]:.3f}in" height="{dims["full_h"]:.3f}in" viewBox="0 0 {width:.3f} {height:.3f}">',
        "<title>Editable full-wrap cover template</title>",
        f'<g id="cover-background" data-editable="true">{svg_rect(0, 0, width, height, colors["primary"], "background-primary")}{svg_rect(0, 0, width, height * 0.28, colors["secondary"], "background-band")}{svg_rect(0, height * 0.88, width, height * 0.12, colors["accent"], "background-footer")}</g>',
        f'<g id="cover-panels" data-editable="true">{svg_rect(back_x + 28.8, bleed + 57.6, trim_w - 57.6, trim_h - 72, colors["secondary"], "back-panel")}{svg_rect(front_x + 28.8, bleed + 57.6, trim_w - 57.6, trim_h - 72, colors["highlight"], "front-panel")}</g>',
        f'<g id="front-text" data-editable="true">{svg_text(center_x, height * 0.42, topic, 32, colors["header_text"], editable_id="front-title", weight="700")}{svg_text(center_x, height * 0.42 + 42, subtitle, 13, colors["text"], editable_id="front-subtitle")}{svg_text(center_x, height - bleed - 30, author, 11, colors["text"], editable_id="front-author")}{svg_text(center_x, height * 0.58, audience, 10, colors["text"], editable_id="front-audience")}</g>',
        f'<g id="back-text" data-editable="true">{svg_text(back_x + trim_w / 2, height * 0.48, blurb, 13, colors["text"], editable_id="back-blurb")}{svg_text(back_x + trim_w / 2, height * 0.32, "Barcode placeholder", 10, colors["dark"], editable_id="barcode-label")}{svg_rect(back_x + trim_w / 2 - 72, height * 0.32 - 28, 144, 42, "#FFFFFF", "barcode-placeholder", colors["line"], "6 4")}</g>',
        f'<g id="spine-text" data-editable="true" transform="translate({spine_x + spine / 2:.3f} {height / 2:.3f}) rotate(-90)">{svg_text(0, 0, spine_text, 10, colors["text"], editable_id="spine-title")}</g>',
        f'<g id="guides" fill="none" stroke="#B42318" stroke-width="1" opacity="0.75">{svg_rect(bleed, bleed, trim_w, trim_h, "none", "back-trim", "#B42318", "8 5")}{svg_rect(spine_x, bleed, spine, trim_h, "none", "spine-guide", "#B42318", "3 3")}{svg_rect(front_x, bleed, trim_w, trim_h, "none", "front-trim", "#B42318", "8 5")}{svg_rect(bleed + safe, bleed + safe, trim_w - 2 * safe, trim_h - 2 * safe, "none", "safe-area", "#B42318", "2 4")}</g>',
        '<text x="12" y="18" font-family="Arial" font-size="9" fill="#B42318">GUIDES: remove before publishing</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def draw_pdf_text(c, x: float, y: float, value: str, size: int, color, align: str = "center", font: str = "Helvetica"):
    c.setFillColor(color)
    c.setFont(font, size)
    if align == "center":
        c.drawCentredString(x, y, value)
    else:
        c.drawString(x, y, value)


def cover_pdf(cfg: dict, dims: dict, colors: dict, output: Path):
    scale = inch
    width = dims["full_w"] * scale
    height = dims["full_h"] * scale
    bleed = BLEED_IN * scale
    trim_w = dims["trim_w"] * scale
    trim_h = dims["trim_h"] * scale
    spine = dims["spine"] * scale
    back_x = bleed
    spine_x = bleed + trim_w
    front_x = spine_x + spine
    c = rl_canvas.Canvas(str(output), pagesize=(width, height))
    c.setTitle(f'{cfg.get("topic", "Daily Planner")} — Editable Cover')
    c.setFillColor(HexColor(colors["primary"]))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(HexColor(colors["secondary"]))
    c.rect(0, height * 0.72, width, height * 0.28, fill=1, stroke=0)
    c.setFillColor(HexColor(colors["accent"]))
    c.rect(0, 0, width, height * 0.12, fill=1, stroke=0)
    c.setFillColor(HexColor(colors["secondary"]))
    c.roundRect(back_x + 0.4 * scale, bleed + 0.8 * scale, trim_w - 0.8 * scale, trim_h - 1.0 * scale, 12, fill=1, stroke=0)
    c.setFillColor(HexColor(colors["highlight"]))
    c.roundRect(front_x + 0.4 * scale, bleed + 0.8 * scale, trim_w - 0.8 * scale, trim_h - 1.0 * scale, 12, fill=1, stroke=0)
    center_x = front_x + trim_w / 2
    topic = cfg.get("topic", "Daily Planner")
    subtitle = cfg.get("subtitle") or f'A thoughtful companion for {cfg.get("niche", "your journey")}'
    author = cfg.get("authorName", "Bright Mindful Pages")
    draw_pdf_text(c, center_x, height * 0.42, topic, 24, HexColor(colors["header_text"]), font="Helvetica-Bold")
    draw_pdf_text(c, center_x, height * 0.42 - 0.42 * scale, subtitle, 11, HexColor(colors["text"]))
    draw_pdf_text(c, center_x, height - bleed - 0.42 * scale, author, 10, HexColor(colors["text"]))
    draw_pdf_text(c, back_x + trim_w / 2, height * 0.48, f'A practical, calming space to support your {cfg.get("niche", "daily")} journey.', 11, HexColor(colors["text"]))
    c.setStrokeColor(HexColor(colors["line"]))
    c.setDash(5, 4)
    c.rect(back_x + 0.5 * scale, height * 0.28, 2.0 * scale, 0.55 * scale, fill=0, stroke=1)
    draw_pdf_text(c, back_x + trim_w / 2, height * 0.25, "Barcode placeholder", 8, HexColor(colors["dark"]))
    if dims["page_count"] >= 79:
        c.saveState()
        c.translate(spine_x + spine / 2, height / 2)
        c.rotate(90)
        draw_pdf_text(c, 0, 0, topic, 8, HexColor(colors["text"]))
        c.restoreState()
    c.setStrokeColor(HexColor("#B42318"))
    c.setDash(6, 4)
    c.rect(bleed, bleed, trim_w, trim_h, fill=0, stroke=1)
    c.rect(front_x, bleed, trim_w, trim_h, fill=0, stroke=1)
    c.setDash(3, 3)
    c.line(spine_x, bleed, spine_x, height - bleed)
    c.line(front_x, bleed, front_x, height - bleed)
    c.setDash(2, 4)
    c.rect(bleed + 0.5 * scale, bleed + 0.5 * scale, trim_w - scale, trim_h - scale, fill=0, stroke=1)
    c.setDash()
    draw_pdf_text(c, 0.16 * scale, height - 0.22 * scale, "GUIDES: remove before publishing", 7, HexColor("#B42318"), align="left")
    c.showPage()
    c.save()


def interior_page_names(cfg: dict) -> list[str]:
    names = ["title", "introduction", "daily-tracker"]
    if cfg.get("includeWeeklyReview") is not False:
        names.append("weekly-review")
    if cfg.get("includeHabitTracker") is not False:
        names.append("habit-tracker")
    names.append("notes")
    return names


def interior_svg(cfg: dict, colors: dict, names: list[str]) -> str:
    trim_w, trim_h = TRIM_SIZES_IN.get(cfg.get("trimSize", "6x9"), TRIM_SIZES_IN["6x9"])
    page_w, page_h = trim_w * 72, trim_h * 72
    gap = 26
    margin = min(page_w, page_h) * 0.09
    content_w = page_w - 2 * margin
    total_h = len(names) * (page_h + gap) + gap
    topic = cfg.get("topic", "Daily Planner")
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_w / 72:.3f}in" height="{total_h / 72:.3f}in" viewBox="0 0 {page_w} {total_h}">', "<title>Editable interior page templates</title>"]
    for index, name in enumerate(names):
        y0 = gap + index * (page_h + gap)
        pieces.append(f'<g id="page-{esc(name)}" data-page-type="{esc(name)}" data-editable="true" transform="translate(0 {y0})">')
        pieces.append(svg_rect(0, 0, page_w, page_h, "#FFFFFF", f"{name}-page"))
        header_y = margin
        header_h = min(42, page_h * 0.065)
        pieces.append(svg_rect(margin, header_y, content_w, header_h, colors["primary"], f"{name}-header"))
        pieces.append(svg_text(page_w / 2, header_y + header_h * 0.67, name.replace("-", " ").title(), min(18, page_w * 0.042), colors["dark"], editable_id=f"{name}-heading", weight="700"))
        pieces.append(svg_text(margin + 8, header_y + header_h + 28, f"Editable {name.replace('-', ' ')} template · {topic}", min(9, page_w * 0.021), colors["text"], anchor="start", editable_id=f"{name}-description"))
        content_top = header_y + header_h + 72
        row_gap = max(28, (page_h - content_top - margin) / 12)
        if name == "title":
            pieces.append(svg_text(page_w / 2, 280, topic, 25, colors["header_text"], editable_id="title-book-name", weight="700"))
            pieces.append(svg_text(page_w / 2, min(page_h - margin - 120, 320), cfg.get("authorName", "Bright Mindful Pages"), 13, colors["text"], editable_id="title-author"))
        elif name == "introduction":
            pieces.append(svg_text(margin, content_top, "How to use this book", 14, colors["header_text"], anchor="start", editable_id="intro-heading", weight="700"))
            for row in range(5):
                pieces.append(svg_rect(margin, content_top + 42 + row * row_gap, content_w, 1, colors["line"], f"intro-line-{row}"))
        elif name == "daily-tracker":
            pieces.append(svg_text(margin, content_top, "Date:", 11, colors["text"], anchor="start", editable_id="daily-date"))
            for row in range(7):
                pieces.append(svg_rect(margin, content_top + 42 + row * row_gap, content_w, 1, colors["line"], f"daily-line-{row}"))
            for column in range(3):
                card_gap = content_w * 0.04
                card_w = (content_w - 2 * card_gap) / 3
                pieces.append(svg_rect(margin + column * (card_w + card_gap), page_h - margin - 80, card_w, 54, colors["secondary"], f"daily-card-{column}"))
        elif name == "weekly-review":
            for row in range(6):
                pieces.append(svg_rect(margin, content_top + row * row_gap, content_w, 1, colors["line"], f"weekly-line-{row}"))
        elif name == "habit-tracker":
            for row in range(7):
                for column in range(5):
                    box = min(18, content_w * 0.055)
                    column_gap = (content_w - 5 * box) / 4
                    pieces.append(svg_rect(margin + column * (box + column_gap), content_top + row * row_gap, box, box, "none", f"habit-check-{row}-{column}", colors["line"]))
        else:
            for row in range(12):
                pieces.append(svg_rect(margin, content_top + row * row_gap, content_w, 1, colors["line"], f"notes-line-{row}"))
        pieces.append(f'<rect x="{margin:.3f}" y="{margin:.3f}" width="{content_w:.3f}" height="{page_h - 2 * margin:.3f}" fill="none" stroke="#B42318" stroke-dasharray="8 5" opacity="0.65"/>')
        pieces.append(f'<text x="{margin + 8:.3f}" y="{page_h - margin / 2:.3f}" font-family="Arial" font-size="8" fill="#B42318">GUIDES: duplicate or edit this page; remove guide before publishing</text>')
        pieces.append("</g>")
    pieces.append("</svg>")
    return "\n".join(pieces)


def interior_pdf(cfg: dict, colors: dict, names: list[str], output: Path):
    trim_w, trim_h = TRIM_SIZES_IN.get(cfg.get("trimSize", "6x9"), TRIM_SIZES_IN["6x9"])
    page_w, page_h = trim_w * inch, trim_h * inch
    margin = min(page_w, page_h) * 0.09
    content_w = page_w - 2 * margin
    c = rl_canvas.Canvas(str(output), pagesize=(page_w, page_h))
    topic = cfg.get("topic", "Daily Planner")
    for name in names:
        c.setFillColor(white)
        c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
        c.setFillColor(HexColor(colors["primary"]))
        header_h = min(0.55 * inch, page_h * 0.065)
        header_y = page_h - margin - header_h
        c.roundRect(margin, header_y, content_w, header_h, 8, fill=1, stroke=0)
        draw_pdf_text(c, page_w / 2, header_y + header_h * 0.58, name.replace("-", " ").title(), 16, HexColor(colors["dark"]), font="Helvetica-Bold")
        draw_pdf_text(c, margin + 8, header_y - 0.28 * inch, f"Editable {name.replace('-', ' ')} template · {topic}", 8, HexColor(colors["text"]), align="left")
        c.setStrokeColor(HexColor(colors["line"]))
        content_top = header_y - 0.85 * inch
        row_gap = max(0.35 * inch, (content_top - margin) / 12)
        if name == "title":
            draw_pdf_text(c, page_w / 2, page_h * 0.52, topic, 23, HexColor(colors["header_text"]), font="Helvetica-Bold")
            draw_pdf_text(c, page_w / 2, page_h * 0.52 - 0.45 * inch, cfg.get("authorName", "Bright Mindful Pages"), 12, HexColor(colors["text"]))
        elif name == "introduction":
            draw_pdf_text(c, margin, content_top, "How to use this book", 12, HexColor(colors["header_text"]), align="left", font="Helvetica-Bold")
            for row in range(5):
                y = content_top - 0.55 * inch - row * row_gap
                c.line(margin, y, margin + content_w, y)
        elif name == "daily-tracker":
            draw_pdf_text(c, margin, content_top, "Date:", 10, HexColor(colors["text"]), align="left")
            for row in range(7):
                y = content_top - 0.55 * inch - row * row_gap
                c.line(margin, y, margin + content_w, y)
        elif name == "habit-tracker":
            box = min(0.22 * inch, content_w * 0.055)
            column_gap = (content_w - 5 * box) / 4
            for row in range(7):
                for column in range(5):
                    x = margin + column * (box + column_gap)
                    y = content_top - row * row_gap
                    c.rect(x, y, box, box, fill=0, stroke=1)
        else:
            for row in range(12):
                y = content_top - row * row_gap
                c.line(margin, y, margin + content_w, y)
        c.setStrokeColor(HexColor("#B42318"))
        c.setDash(5, 4)
        c.rect(margin, margin, content_w, page_h - 2 * margin, fill=0, stroke=1)
        c.setDash()
        draw_pdf_text(c, margin + 8, margin / 2, "GUIDES: duplicate or edit this page; remove guide before publishing", 7, HexColor("#B42318"), align="left")
        c.showPage()
    c.save()


def readme(cfg: dict, dims: dict, names: list[str]) -> str:
    topic = cfg.get("topic", "Daily Planner")
    return f"""# Editable template package: {topic}

This package contains editable vector assets for Canva and Affinity.

## Files

- `cover/cover.svg` — editable full-wrap cover with back, spine, front, bleed, trim, safe-area, and barcode guides.
- `cover/cover.pdf` — vector PDF version of the cover.
- `interior/interior-template.svg` — reusable editable page templates stacked in one SVG artboard.
- `interior/interior-template.pdf` — vector PDF with one page per reusable template.
- `template.json` — dimensions, page count, palette, and export metadata.

Interior templates included: {", ".join(names)}.

## Workflow

1. Import the SVG or PDF into Canva or Affinity.
2. Edit elements marked as editable and duplicate interior pages as needed.
3. Remove red guide lines, placeholder labels, and barcode placeholder before publishing.
4. Use the existing KDP-ready PDF generator for the final upload file when you do not need edits.

This export does not create native `.canva` or `.afdesign` files.
"""


def generate(cfg: dict, output_path: str):
    dims = dimensions(cfg)
    colors = PALETTES.get(cfg.get("colorPalette", "lavender_mint"), PALETTES["lavender_mint"])
    names = interior_page_names(cfg)
    output = Path(output_path)
    work_dir = Path(tempfile.mkdtemp(prefix="editable-template-"))
    package_dir = work_dir / f"{safe_topic(cfg.get('topic', 'Daily Planner'))}-editable-template"
    try:
        (package_dir / "cover").mkdir(parents=True)
        (package_dir / "interior").mkdir(parents=True)
        (package_dir / "cover" / "cover.svg").write_text(cover_svg(cfg, dims, colors), encoding="utf-8")
        cover_pdf(cfg, dims, colors, package_dir / "cover" / "cover.pdf")
        (package_dir / "interior" / "interior-template.svg").write_text(interior_svg(cfg, colors, names), encoding="utf-8")
        interior_pdf(cfg, colors, names, package_dir / "interior" / "interior-template.pdf")

        metadata = {
            "formatVersion": "1.0",
            "topic": cfg.get("topic", "Daily Planner"),
            "niche": cfg.get("niche", ""),
            "targetAudience": cfg.get("targetAudience", ""),
            "authorName": cfg.get("authorName", ""),
            "subtitle": cfg.get("subtitle") or "",
            "bookType": cfg.get("bookType") or "",
            "trimSize": cfg.get("trimSize", "6x9"),
            "trimWidthInches": dims["trim_w"],
            "trimHeightInches": dims["trim_h"],
            "bleedInches": BLEED_IN,
            "safeAreaInches": SAFE_INSET_IN,
            "pageCount": dims["page_count"],
            "spineWidthInches": dims["spine"],
            "paperType": dims["paper"],
            "colorPalette": cfg.get("colorPalette", "lavender_mint"),
            "palette": colors,
            "fontFamily": "Arial / Helvetica",
            "interiorTemplatePages": names,
        }
        (package_dir / "template.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        (package_dir / "README.md").write_text(readme(cfg, dims, names), encoding="utf-8")

        output.parent.mkdir(parents=True, exist_ok=True)
        temp_zip = output.with_suffix(output.suffix + ".tmp")
        if temp_zip.exists():
            temp_zip.unlink()
        with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in sorted(package_dir.rglob("*")):
                if file_path.is_file():
                    archive.write(file_path, file_path.relative_to(work_dir).as_posix())
        os.replace(temp_zip, output)
        files = [str(path.relative_to(package_dir)).replace(os.sep, "/") for path in sorted(package_dir.rglob("*")) if path.is_file()]
        return {
            "success": True,
            "pageCount": dims["page_count"],
            "cover": {
                "widthInches": round(dims["full_w"], 4),
                "heightInches": round(dims["full_h"], 4),
                "spineInches": round(dims["spine"], 4),
            },
            "files": files,
        }
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def main():
    try:
        if len(sys.argv) != 3:
            raise ValueError("Expected JSON config and output ZIP path")
        result = generate(json.loads(sys.argv[1]), sys.argv[2])
        print(json.dumps(result))
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()