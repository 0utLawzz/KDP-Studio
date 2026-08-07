#!/usr/bin/env python3
"""
KDP Full-Wrap Cover Generator — Bright Mindful Pages
Generates KDP-compliant full-wrap covers (front + spine + back) as single PDF.
MARGIN: 0.4in on all sides (fixed — never change).
Spine width: page_count / 110 inches (KDP standard).
"""

import sys
import os
import json
import argparse
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from text_bounds import validate_text_bounds

MARGIN = 0.4 * inch   # Fixed — do not change
PAGES_PER_INCH = 110  # KDP standard
BLEED = 0.125 * inch  # KDP required bleed on all edges

TRIM_SIZES = {
    "6x9": (6.0, 9.0),
    "5x8": (5.0, 8.0),
    "8.5x11": (8.5, 11.0),
}

PALETTES = {
    "lavender_mint": {
        "primary": "#C9B8E8", "secondary": "#A8D8C8", "accent": "#E8D5F0",
        "highlight": "#F5F0FF", "text": "#4A4A6A", "header_text": "#FFFFFF",
    },
    "sage_teal": {
        "primary": "#7BA08C", "secondary": "#5B8FA8", "accent": "#A8C5B5",
        "highlight": "#F0F7F4", "text": "#2D4A3E", "header_text": "#FFFFFF",
    },
    "rose_gold": {
        "primary": "#C4847A", "secondary": "#D4A8A0", "accent": "#F0D0CC",
        "highlight": "#FDF5F4", "text": "#5A2D2D", "header_text": "#FFFFFF",
    },
    "ocean_breeze": {
        "primary": "#6B9DC2", "secondary": "#89C4D4", "accent": "#B8DDE8",
        "highlight": "#F0F8FF", "text": "#1A3D5C", "header_text": "#FFFFFF",
    },
    "sunset_peach": {
        "primary": "#E8956D", "secondary": "#F4B896", "accent": "#FAD5B8",
        "highlight": "#FFF5EE", "text": "#6B3020", "header_text": "#FFFFFF",
    },
    "forest_fern": {
        "primary": "#5B8C5A", "secondary": "#7BAF7A", "accent": "#A8CCA8",
        "highlight": "#F0F7F0", "text": "#1F3D1F", "header_text": "#FFFFFF",
    },
    "dusty_plum": {
        "primary": "#8B6B8B", "secondary": "#A88BA8", "accent": "#C8A8C8",
        "highlight": "#F5EEF5", "text": "#3D1F3D", "header_text": "#FFFFFF",
    },
    "golden_hour": {
        "primary": "#D4A843", "secondary": "#E8C878", "accent": "#F5E0A0",
        "highlight": "#FFFBF0", "text": "#5A3C00", "header_text": "#FFFFFF",
    },
    "arctic_blue": {
        "primary": "#7098B8", "secondary": "#90B8D8", "accent": "#B8D5E8",
        "highlight": "#F0F5FF", "text": "#1A2D4A", "header_text": "#FFFFFF",
    },
    "terracotta": {
        "primary": "#C4714A", "secondary": "#D89070", "accent": "#EBB898",
        "highlight": "#FDF2EC", "text": "#5C2010", "header_text": "#FFFFFF",
    },
    "mint_chocolate": {
        "primary": "#6BAA8C", "secondary": "#8B5A3C", "accent": "#A8D5C0",
        "highlight": "#F0FFF8", "text": "#1C3D2D", "header_text": "#FFFFFF",
    },
    "bright_momentum": {
        "primary": "#275DA8", "secondary": "#2FA594", "accent": "#FFD45C",
        "highlight": "#F8FFF8", "text": "#173B45", "header_text": "#FFFFFF",
        "coral": "#FF6D5C",
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


def hex_color(h):
    return colors.HexColor(h)


def get_palette(key):
    raw = PALETTES.get(key, PALETTES["lavender_mint"])
    return {k: hex_color(v) if k != "name" else v for k, v in raw.items()}


def wrap_text(c, text, font, size, max_width):
    """Return word-wrapped lines whose measured widths fit max_width."""
    words = text.split()
    if not words:
        return []

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if c.stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_bright_momentum_front(c, p, front_start, front_width, total_h, title, subtitle, author, day_count):
    """Draw the approved cobalt, coral, mint, and yellow front-cover lockup."""
    safe_left = front_start + MARGIN
    safe_right = front_start + front_width - MARGIN
    front_cx = front_start + front_width / 2
    coral = p["coral"]
    yellow = p["accent"]
    mint = p["secondary"]

    c.setFillColor(p["primary"])
    c.rect(front_start, 0, front_width, total_h, fill=1, stroke=0)

    # Bright dotted path gives the cover a strong thumbnail silhouette.
    dots = [
        (0.28, 0.95, 0.14), (0.54, 0.80, 0.16), (0.80, 0.65, 0.15),
        (1.06, 0.51, 0.17), (1.32, 0.38, 0.13),
    ]
    for x_in, y_ratio, radius_in in dots:
        c.setFillColor(yellow)
        c.circle(front_start + x_in * inch, total_h * y_ratio, radius_in * inch, fill=1, stroke=0)

    c.setFillColor(p["header_text"])
    c.setFont("Helvetica-Bold", 8)
    validate_text_bounds(
        c, "BMP", "Helvetica-Bold", 8, ("left", safe_left),
        safe_left, safe_right, "bright-momentum brand mark",
    )
    c.drawString(safe_left, total_h - MARGIN - 0.2 * inch, "BMP")

    c.setFillColor(colors.Color(1, 1, 1, alpha=0.82))
    c.setFont("Helvetica", 6.5)
    validate_text_bounds(
        c, author.upper(), "Helvetica", 6.5, ("left", safe_left),
        safe_left, safe_right, "bright-momentum author line",
    )
    c.drawString(safe_left, total_h * 0.59, author.upper())

    words = title.strip().split()
    first_line = words[0] if words else "SOBRIETY"
    second_line = " ".join(words[1:]) if len(words) > 1 else ""
    title_size = 25 if front_width >= 6 * inch else 20
    title_y = total_h * 0.51
    c.setFont("Helvetica-Bold", title_size)
    c.setFillColor(p["header_text"])
    validate_text_bounds(
        c, first_line.upper(), "Helvetica-Bold", title_size, ("left", safe_left),
        safe_left, safe_right, "bright-momentum title first line",
    )
    c.drawString(safe_left, title_y, first_line.upper())
    if second_line:
        c.setFillColor(mint)
        validate_text_bounds(
            c, second_line.upper(), "Helvetica-Bold", title_size, ("left", safe_left),
            safe_left, safe_right, "bright-momentum title second line",
        )
        c.drawString(safe_left, title_y - title_size - 3, second_line.upper())

    c.setFillColor(yellow)
    c.rect(safe_left, title_y - title_size - 0.24 * inch, 0.58 * inch, 0.045 * inch, fill=1, stroke=0)
    c.setFillColor(coral)
    c.roundRect(safe_left, title_y - title_size - 0.38 * inch, 1.1 * inch, 0.08 * inch, 4, fill=1, stroke=0)

    subtitle_text = subtitle.strip() or f"{day_count}-Day Daily Tracker"
    c.setFillColor(p["header_text"])
    c.setFont("Helvetica-Bold", 9)
    validate_text_bounds(
        c, subtitle_text[:48], "Helvetica-Bold", 9, ("left", safe_left),
        safe_left, safe_right, "bright-momentum subtitle",
    )
    c.drawString(safe_left, title_y - title_size - 0.53 * inch, subtitle_text[:48])

    badge_r = 0.54 * inch
    badge_cx = safe_right - badge_r
    badge_cy = total_h * 0.27
    c.setFillColor(yellow)
    c.circle(badge_cx, badge_cy, badge_r, fill=1, stroke=0)
    c.setFillColor(p["text"])
    c.setFont("Helvetica-Bold", 7)
    validate_text_bounds(
        c, "ONE DAY", "Helvetica-Bold", 7, badge_cx,
        safe_left, safe_right, "bright-momentum badge line one",
    )
    c.drawCentredString(badge_cx, badge_cy + 0.05 * inch, "ONE DAY")
    validate_text_bounds(
        c, "AT A TIME", "Helvetica-Bold", 7, badge_cx,
        safe_left, safe_right, "bright-momentum badge line two",
    )
    c.drawCentredString(badge_cx, badge_cy - 0.08 * inch, "AT A TIME")

    c.setFillColor(colors.Color(1, 1, 1, alpha=0.75))
    c.setFont("Helvetica", 6.5)
    validate_text_bounds(
        c, "A practical journal for steady, hopeful progress",
        "Helvetica", 6.5, ("left", safe_left), safe_left, safe_right,
        "bright-momentum footer",
    )
    c.drawString(safe_left, MARGIN + 0.18 * inch, "A practical journal for steady, hopeful progress")


def generate_cover(args, output_path):
    palette_key = args.color_palette or "lavender_mint"
    p = get_palette(palette_key)
    trim_w, trim_h = TRIM_SIZES.get(args.trim_size or "6x9", TRIM_SIZES["6x9"])
    trim_w_pt = trim_w * inch
    trim_h_pt = trim_h * inch
    page_count = int(args.page_count or 72)
    spine_in = page_count / PAGES_PER_INCH
    spine_pt = spine_in * inch

    # Full wrap: back + spine + front + bleeds on all edges
    total_w = (trim_w * 2 + spine_in) * inch + 2 * BLEED
    total_h = trim_h * inch + 2 * BLEED

    c = canvas.Canvas(output_path, pagesize=(total_w, total_h))

    back_start = BLEED
    spine_start = BLEED + trim_w_pt
    front_start = spine_start + spine_pt

    # ── Background gradient effect (solid fill per zone) ─────────────────────
    # Back cover
    c.setFillColor(p["secondary"])
    c.rect(0, 0, spine_start, total_h, fill=1, stroke=0)

    # Spine
    c.setFillColor(p["primary"])
    c.rect(spine_start, 0, spine_pt, total_h, fill=1, stroke=0)

    # Front cover
    c.setFillColor(p["accent"])
    c.rect(front_start, 0, trim_w_pt + BLEED, total_h, fill=1, stroke=0)

    # Front cover — decorative header band
    header_h = total_h * 0.45
    c.setFillColor(p["primary"])
    c.rect(front_start, total_h - header_h, trim_w_pt + BLEED, header_h, fill=1, stroke=0)

    # Front cover — decorative stripe
    c.setFillColor(p["secondary"])
    c.rect(front_start, total_h - header_h - 0.12 * inch, trim_w_pt + BLEED, 0.12 * inch, fill=1, stroke=0)

    # ── Front cover text ──────────────────────────────────────────────────────
    title = args.title or "My Daily Planner"
    subtitle = args.subtitle or ""
    author = args.author_name or "Bright Mindful Pages"
    day_count = int(args.day_count or 60)

    front_cx = front_start + trim_w_pt / 2

    if palette_key == "bright_momentum":
        draw_bright_momentum_front(
            c, p, front_start, trim_w_pt + BLEED, total_h,
            title, subtitle, author, day_count,
        )
    else:
        # Preserve the established cover treatment for other palettes.
        c.setFillColor(p["header_text"])
        title_max_w = trim_w_pt - 2 * MARGIN
        font_size = 28
        lines = wrap_text(c, title, "Helvetica-Bold", font_size, title_max_w)
        while (
            (len(lines) > 3
             or any(c.stringWidth(line, "Helvetica-Bold", font_size) > title_max_w for line in lines))
            and font_size > 8
        ):
            font_size -= 2
            lines = wrap_text(c, title, "Helvetica-Bold", font_size, title_max_w)

        if (
            len(lines) > 3
            or any(c.stringWidth(line, "Helvetica-Bold", font_size) > title_max_w for line in lines)
        ):
            raise ValueError(
                f"Title cannot fit within the {title_max_w / inch:.2f}-inch safe width "
                f"at the minimum font size: {title!r}"
            )

        title_y = total_h - header_h * 0.35
        title_bounds = []
        for i, line in enumerate(lines):
            line_width = c.stringWidth(line, "Helvetica-Bold", font_size)
            line_left = front_cx - line_width / 2
            line_right = front_cx + line_width / 2
            validate_text_bounds(
                c, line, "Helvetica-Bold", font_size, front_cx,
                front_start + MARGIN, front_start + trim_w_pt - MARGIN,
                f"front-cover title line {i + 1}",
            )
            c.drawCentredString(front_cx, title_y - i * (font_size + 4), line)
            title_bounds.append((line, line_left, line_right))

        safe_left = front_start + MARGIN
        safe_right = front_start + trim_w_pt - MARGIN
        assert all(
            line_left >= safe_left and line_right <= safe_right
            for _, line_left, line_right in title_bounds
        ), (
            "A centered title line crosses the front-cover safe margin: "
            f"{title_bounds!r}; expected {safe_left:.2f}-{safe_right:.2f}pt"
        )

        if subtitle:
            c.setFillColor(p["header_text"])
            c.setFont("Helvetica", 11)
            validate_text_bounds(
                c, subtitle, "Helvetica", 11, front_cx,
                front_start + MARGIN, front_start + trim_w_pt - MARGIN,
                "front-cover subtitle",
            )
            c.drawCentredString(front_cx, total_h - header_h - 0.35 * inch, subtitle)

        badge_y = total_h - header_h - 0.85 * inch
        c.setFillColor(p["secondary"])
        c.roundRect(front_cx - 0.7 * inch, badge_y - 0.15 * inch, 1.4 * inch, 0.35 * inch, 8, fill=1, stroke=0)
        c.setFillColor(p["header_text"])
        c.setFont("Helvetica-Bold", 10)
        validate_text_bounds(
            c, f"{day_count}-Day Journey", "Helvetica-Bold", 10, front_cx,
            front_start + MARGIN, front_start + trim_w_pt - MARGIN,
            "front-cover journey badge",
        )
        c.drawCentredString(front_cx, badge_y + 0.04 * inch, f"{day_count}-Day Journey")

        c.setFillColor(p["secondary"])
        c.setStrokeColor(p["secondary"])
        c.setLineWidth(0)
        circle_data = [(front_start + 0.2 * inch, BLEED + 0.2 * inch, 0.15), (front_start + trim_w_pt - 0.2 * inch, BLEED + 0.2 * inch, 0.12)]
        for cx, cy, r in circle_data:
            c.setFillColor(colors.Color(p["secondary"].red, p["secondary"].green, p["secondary"].blue, 0.4))
            c.circle(cx, cy, r * inch, fill=1, stroke=0)

        c.setFillColor(p["text"])
        c.setFont("Helvetica", 9)
        validate_text_bounds(
            c, author, "Helvetica", 9, front_cx,
            front_start + MARGIN, front_start + trim_w_pt - MARGIN,
            "front-cover author line",
        )
        c.drawCentredString(front_cx, BLEED + 0.3 * inch, author)

    # ── Spine text (only if page_count >= 79) ─────────────────────────────────
    if page_count >= 79:
        c.saveState()
        spine_cx = spine_start + spine_pt / 2
        c.translate(spine_cx, total_h / 2)
        c.rotate(90)
        c.setFillColor(p["header_text"])
        spine_font_size = min(10, spine_pt / inch * 6)
        c.setFont("Helvetica-Bold", spine_font_size)
        short_title = title if len(title) <= 30 else title[:27] + "..."
        validate_text_bounds(
            c, short_title, "Helvetica-Bold", spine_font_size, total_h / 2,
            MARGIN, total_h - MARGIN, "spine title",
        )
        c.drawCentredString(0, 0, short_title)
        c.setFont("Helvetica", spine_font_size * 0.8)
        validate_text_bounds(
            c, author, "Helvetica", spine_font_size * 0.8, total_h / 2,
            MARGIN, total_h - MARGIN, "spine author line",
        )
        c.drawCentredString(0, -(spine_font_size + 3), author)
        c.restoreState()

    # ── Back cover ────────────────────────────────────────────────────────────
    back_cx = BLEED + trim_w_pt / 2

    # Back cover — description / blurb
    c.setFillColor(p["text"])
    c.setFont("Helvetica-Bold", 12)
    validate_text_bounds(
        c, "About This Planner", "Helvetica-Bold", 12, back_cx,
        back_start + MARGIN, spine_start - MARGIN, "back-cover heading",
    )
    c.drawCentredString(back_cx, total_h - BLEED - 0.5 * inch, "About This Planner")

    blurb = (
        f"Make space for steady progress with this {day_count}-day "
        "recovery tracker. Each page helps you notice bright spots, "
        "honor your support system, and choose one next right step. "
        "A practical journal for hopeful, intentional progress."
        if palette_key == "bright_momentum"
        else (
            f"Transform your daily routine with this {day_count}-day "
            "structured planner. Each page is thoughtfully designed to help "
            "you set intentions, track progress, and reflect on your journey. "
            "Ideal for anyone ready to build better habits and live more intentionally."
        )
    )

    c.setFont("Helvetica", 9)
    blurb_words = blurb.split()
    blurb_lines = []
    bl_current = ""
    max_w = trim_w_pt - 0.8 * inch
    for word in blurb_words:
        test = (bl_current + " " + word).strip()
        if c.stringWidth(test, "Helvetica", 9) > max_w:
            blurb_lines.append(bl_current)
            bl_current = word
        else:
            bl_current = test
    if bl_current:
        blurb_lines.append(bl_current)

    y = total_h - BLEED - 1.0 * inch
    for line in blurb_lines:
        validate_text_bounds(
            c, line, "Helvetica", 9, back_cx,
            back_start + MARGIN, spine_start - MARGIN, "back-cover blurb",
        )
        c.drawCentredString(back_cx, y, line)
        y -= 0.2 * inch

    # Barcode placeholder
    c.setFillColor(colors.white)
    c.rect(back_cx - 0.65 * inch, BLEED + 0.15 * inch, 1.3 * inch, 0.8 * inch, fill=1, stroke=0)
    c.setFillColor(p["text"])
    c.setFont("Helvetica", 6)
    validate_text_bounds(
        c, "ISBN barcode here", "Helvetica", 6, back_cx,
        back_start + MARGIN, spine_start - MARGIN, "back-cover barcode label",
    )
    c.drawCentredString(back_cx, BLEED + 0.08 * inch, "ISBN barcode here")

    # Publisher name
    c.setFont("Helvetica-Bold", 8)
    validate_text_bounds(
        c, author, "Helvetica-Bold", 8, back_cx,
        back_start + MARGIN, spine_start - MARGIN, "back-cover author line",
    )
    c.drawCentredString(back_cx, BLEED + 1.1 * inch, author)

    c.save()
    return spine_in


def main():
    parser = argparse.ArgumentParser(description="Generate KDP full-wrap cover PDF")
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="My Daily Planner")
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--author-name", default="Bright Mindful Pages")
    parser.add_argument("--color-palette", default="lavender_mint")
    parser.add_argument("--trim-size", default="6x9", choices=["6x9", "5x8", "8.5x11"])
    parser.add_argument("--page-count", type=int, default=72)
    parser.add_argument("--day-count", type=int, default=60)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    spine_in = generate_cover(args, args.output)

    result = {
        "success": True,
        "spine_inches": round(spine_in, 3),
        "output": args.output,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
