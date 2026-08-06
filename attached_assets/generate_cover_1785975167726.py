#!/usr/bin/env python3
"""
KDP Paperback Cover Generator
Generates a full-wrap cover PDF (back + spine + front) with bleed.

Usage: python3 generate_cover.py '<json_config>' <output_path>

Config keys:
  topic, subtitle, authorName, niche, targetAudience,
  trimSize ("6x9"|"5x8"|"8.5x11"),
  interiorType ("full_color"|"black_white"),
  colorPalette, pageCount (required for spine),
  paperType optional: white|cream|premium_color|standard_color
"""

import sys
import json
from reportlab.lib.pagesizes import inch
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.pdfgen import canvas as rl_canvas

BLEED = 0.125 * inch  # KDP required bleed each side

# Spine multipliers (inches per page) — KDP official
SPINE_MULTIPLIER = {
    "white": 0.002252,
    "cream": 0.0025,
    "standard_color": 0.002252,
    "premium_color": 0.002347,
}

TRIM_SIZES = {
    "6x9": (6 * inch, 9 * inch),
    "5x8": (5 * inch, 8 * inch),
    "8.5x11": (8.5 * inch, 11 * inch),
}

PALETTES = {
    "lavender_mint": {
        "primary": HexColor("#E6D9F7"),
        "secondary": HexColor("#D6F3E8"),
        "accent": HexColor("#FBD6E3"),
        "highlight": HexColor("#D9EEFB"),
        "text": HexColor("#4A3F55"),
        "header_text": HexColor("#6B5580"),
        "dark": HexColor("#3D2F4A"),
        "line": HexColor("#C4B8D4"),
    },
    "ocean_peach": {
        "primary": HexColor("#D9EEFB"),
        "secondary": HexColor("#FFE3D1"),
        "accent": HexColor("#B8D8F0"),
        "highlight": HexColor("#FFDFC4"),
        "text": HexColor("#2D4A5E"),
        "header_text": HexColor("#2D6080"),
        "dark": HexColor("#1A3344"),
        "line": HexColor("#A8C8E0"),
    },
    "sky_pink": {
        "primary": HexColor("#FBD6E3"),
        "secondary": HexColor("#D9EEFB"),
        "accent": HexColor("#E6D9F7"),
        "highlight": HexColor("#FFE3D1"),
        "text": HexColor("#5C2D4E"),
        "header_text": HexColor("#8B3060"),
        "dark": HexColor("#3A1A30"),
        "line": HexColor("#E0A0BC"),
    },
    "forest_earth": {
        "primary": HexColor("#D8EAD4"),
        "secondary": HexColor("#F5E6D0"),
        "accent": HexColor("#B8D4C0"),
        "highlight": HexColor("#EAD8C4"),
        "text": HexColor("#2C3E28"),
        "header_text": HexColor("#3A5C34"),
        "dark": HexColor("#1E2A1A"),
        "line": HexColor("#8EAA86"),
    },
    # BMP-002: Sobriety & Recovery — calm growth palette
    "sage_teal": {
        "primary": HexColor("#C9DCC5"),
        "secondary": HexColor("#BEE3DB"),
        "accent": HexColor("#F0D3D8"),
        "highlight": HexColor("#F2E4D0"),
        "text": HexColor("#4A3F55"),
        "header_text": HexColor("#3A6B50"),
        "dark": HexColor("#2E5842"),
        "line": HexColor("#9ABEA8"),
    },
    # BMP-003: Chronic Pain & Fatigue — gentle low-stimulation palette
    "lavender_grey": {
        "primary": HexColor("#E6D9F7"),
        "secondary": HexColor("#DCE3EA"),
        "accent": HexColor("#D6F3E8"),
        "highlight": HexColor("#FFE3D1"),
        "text": HexColor("#4A3F55"),
        "header_text": HexColor("#5A6A8A"),
        "dark": HexColor("#46536E"),
        "line": HexColor("#B0BEC5"),
    },
    "cobalt_coral": {
        "primary": HexColor("#BFDBFE"),
        "secondary": HexColor("#FDA4AF"),
        "accent": HexColor("#FDE68A"),
        "highlight": HexColor("#DBEAFE"),
        "text": HexColor("#172554"),
        "header_text": HexColor("#1D4ED8"),
        "dark": HexColor("#1E3A8A"),
        "line": HexColor("#93C5FD"),
    },
    "sunshine_mint": {
        "primary": HexColor("#FEF08A"),
        "secondary": HexColor("#A7F3D0"),
        "accent": HexColor("#BAE6FD"),
        "highlight": HexColor("#ECFCCB"),
        "text": HexColor("#14532D"),
        "header_text": HexColor("#166534"),
        "dark": HexColor("#14532D"),
        "line": HexColor("#86EFAC"),
    },
    "berry_pop": {
        "primary": HexColor("#F9A8D4"),
        "secondary": HexColor("#C4B5FD"),
        "accent": HexColor("#FED7AA"),
        "highlight": HexColor("#FCE7F3"),
        "text": HexColor("#581C87"),
        "header_text": HexColor("#9D174D"),
        "dark": HexColor("#581C87"),
        "line": HexColor("#D8B4FE"),
    },
    "ocean_lime": {
        "primary": HexColor("#7DD3FC"),
        "secondary": HexColor("#BEF264"),
        "accent": HexColor("#99F6E4"),
        "highlight": HexColor("#DBEAFE"),
        "text": HexColor("#082F49"),
        "header_text": HexColor("#0369A1"),
        "dark": HexColor("#082F49"),
        "line": HexColor("#67E8F9"),
    },
    "tangerine_sky": {
        "primary": HexColor("#FDBA74"),
        "secondary": HexColor("#7DD3FC"),
        "accent": HexColor("#FEF3C7"),
        "highlight": HexColor("#E0F2FE"),
        "text": HexColor("#172554"),
        "header_text": HexColor("#C2410C"),
        "dark": HexColor("#172554"),
        "line": HexColor("#93C5FD"),
    },
}


def resolve_paper(interior_type: str, paper_type: str | None) -> str:
    if paper_type and paper_type in SPINE_MULTIPLIER:
        return paper_type
    if interior_type == "full_color":
        return "premium_color"
    return "white"


def compute_dimensions(cfg: dict):
    trim_key = cfg.get("trimSize", "6x9")
    trim_w, trim_h = TRIM_SIZES.get(trim_key, TRIM_SIZES["6x9"])
    page_count = int(cfg.get("pageCount", 72))
    paper = resolve_paper(cfg.get("interiorType", "full_color"), cfg.get("paperType"))
    spine = page_count * SPINE_MULTIPLIER[paper] * inch

    # Full cover including bleed
    full_w = BLEED + trim_w + spine + trim_w + BLEED
    full_h = BLEED + trim_h + BLEED

    return {
        "trim_w": trim_w,
        "trim_h": trim_h,
        "spine": spine,
        "full_w": full_w,
        "full_h": full_h,
        "page_count": page_count,
        "paper": paper,
        "spine_inches": page_count * SPINE_MULTIPLIER[paper],
        "full_w_inches": full_w / inch,
        "full_h_inches": full_h / inch,
    }


def wrap_text(c, text, font, size, max_width):
    """Simple word-wrap returning list of lines that fit max_width."""
    words = text.split()
    if not words:
        return []
    lines = []
    current = words[0]
    for w in words[1:]:
        test = current + " " + w
        if c.stringWidth(test, font, size) <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines


def draw_centered_lines(c, lines, y_start, font, size, color, line_gap, page_cx):
    c.setFont(font, size)
    c.setFillColor(color)
    y = y_start
    for line in lines:
        c.drawCentredString(page_cx, y, line)
        y -= line_gap
    return y


def generate(cfg, output_path):
    dims = compute_dimensions(cfg)
    palette_key = cfg.get("colorPalette", "lavender_mint")
    colors = PALETTES.get(palette_key, PALETTES["lavender_mint"])

    topic = cfg.get("topic", "Daily Planner")
    subtitle = cfg.get("subtitle") or f"A thoughtful companion for {cfg.get('niche', 'your journey')}"
    author = cfg.get("authorName", "Bright Mindful Pages")
    niche = cfg.get("niche", "")
    audience = cfg.get("targetAudience", "")
    page_count = dims["page_count"]
    spine_ok = page_count >= 79  # KDP spine text minimum

    full_w = dims["full_w"]
    full_h = dims["full_h"]
    trim_w = dims["trim_w"]
    trim_h = dims["trim_h"]
    spine_w = dims["spine"]

    # Panel x origins (left → right: bleed | back | spine | front | bleed)
    back_x = BLEED
    spine_x = BLEED + trim_w
    front_x = BLEED + trim_w + spine_w
    content_bottom = BLEED
    content_top = full_h - BLEED

    c = rl_canvas.Canvas(output_path, pagesize=(full_w, full_h))
    c.setTitle(f"{topic} — Cover")
    c.setAuthor(author)

    # ── Full background (extends into bleed) ──────────────────────────────────
    c.setFillColor(colors["primary"])
    c.rect(0, 0, full_w, full_h, fill=1, stroke=0)

    # Soft secondary bands on back & front for visual interest
    c.setFillColor(colors["secondary"])
    band_h = full_h * 0.28
    c.rect(0, full_h - band_h, full_w, band_h, fill=1, stroke=0)
    c.setFillColor(colors["accent"])
    c.rect(0, 0, full_w, full_h * 0.12, fill=1, stroke=0)

    # ── BACK COVER ────────────────────────────────────────────────────────────
    back_cx = back_x + trim_w / 2
    safe_inset = 0.5 * inch  # stay inside trim + barcode safety

    # Accent rounded panel
    panel_m = 0.4 * inch
    c.setFillColor(colors["secondary"])
    c.roundRect(
        back_x + panel_m,
        content_bottom + panel_m + 0.8 * inch,
        trim_w - 2 * panel_m,
        trim_h - 2 * panel_m - 1.0 * inch,
        12,
        fill=1,
        stroke=0,
    )

    # Back blurb
    blurb = (
        f"This {page_count}-page undated planner was created for "
        f"{audience or 'anyone'} navigating {niche or 'life'} with intention. "
        f"Start any day. Restart any time. No guilt — just progress."
    )
    max_text_w = trim_w - 2 * panel_m - 0.5 * inch
    blurb_lines = wrap_text(c, blurb, "Helvetica", 10, max_text_w)
    y = content_top - 1.4 * inch
    c.setFillColor(colors["text"])
    c.setFont("Helvetica", 10)
    for line in blurb_lines:
        c.drawCentredString(back_cx, y, line)
        y -= 14

    y -= 18
    features = [
        "✓ Undated daily spreads",
        "✓ Habit & weekly review pages",
        "✓ Soft, calming design",
        "✓ Print-ready KDP interior",
    ]
    c.setFont("Helvetica", 10)
    for feat in features:
        c.drawCentredString(back_cx, y, feat)
        y -= 16

    # Author on back bottom
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors["header_text"])
    c.drawCentredString(back_cx, content_bottom + 1.1 * inch, f"— {author} —")

    # Barcode placeholder zone (bottom-right of back, KDP reserved)
    # Leave empty white-ish box so user can see the reserved area
    bc_w, bc_h = 2.0 * inch, 1.2 * inch
    bc_x = back_x + trim_w - bc_w - 0.35 * inch
    bc_y = content_bottom + 0.25 * inch
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(colors["line"])
    c.setLineWidth(0.5)
    c.rect(bc_x, bc_y, bc_w, bc_h, fill=1, stroke=1)
    c.setFillColor(colors["line"])
    c.setFont("Helvetica", 7)
    c.drawCentredString(bc_x + bc_w / 2, bc_y + bc_h / 2 - 3, "ISBN / Barcode area")

    # ── SPINE ─────────────────────────────────────────────────────────────────
    if spine_w > 0.15 * inch:
        # Spine background strip
        c.setFillColor(colors["dark"])
        c.rect(spine_x, 0, spine_w, full_h, fill=1, stroke=0)

        if spine_ok and spine_w >= 0.25 * inch:
            # Vertical text (rotated)
            c.saveState()
            spine_cx = spine_x + spine_w / 2
            spine_cy = full_h / 2
            c.translate(spine_cx, spine_cy)
            c.rotate(90)
            # After rotate: x is along spine height, y is across spine width
            font_size = 9 if spine_w < 0.4 * inch else 11
            c.setFont("Helvetica-Bold", font_size)
            c.setFillColor(white)
            # Title
            title_w = c.stringWidth(topic, "Helvetica-Bold", font_size)
            max_spine_text = trim_h - 1.0 * inch
            display_title = topic
            if title_w > max_spine_text:
                # Truncate
                while c.stringWidth(display_title + "…", "Helvetica-Bold", font_size) > max_spine_text and len(display_title) > 3:
                    display_title = display_title[:-1]
                display_title += "…"
            c.drawCentredString(0, -font_size / 3, display_title)
            c.restoreState()
        else:
            # Too thin or <79 pages — no text, solid color only
            pass

    # ── FRONT COVER ───────────────────────────────────────────────────────────
    front_cx = front_x + trim_w / 2

    # Decorative top accent bar (inside trim)
    c.setFillColor(colors["accent"])
    c.roundRect(
        front_x + 0.35 * inch,
        content_top - 0.9 * inch,
        trim_w - 0.7 * inch,
        0.55 * inch,
        8,
        fill=1,
        stroke=0,
    )

    # Title
    title_max_w = trim_w - 0.9 * inch
    title_size = 28
    title_lines = wrap_text(c, topic, "Helvetica-Bold", title_size, title_max_w)
    while len(title_lines) > 3 and title_size > 18:
        title_size -= 2
        title_lines = wrap_text(c, topic, "Helvetica-Bold", title_size, title_max_w)

    y = content_top - 1.8 * inch
    y = draw_centered_lines(
        c, title_lines, y, "Helvetica-Bold", title_size, colors["header_text"], title_size + 6, front_cx
    )

    # Decorative dots
    y -= 0.25 * inch
    for i in range(5):
        dx = front_cx - 0.8 * inch + i * 0.4 * inch
        c.setFillColor(colors["secondary"])
        c.circle(dx, y, 4, fill=1, stroke=0)

    # Subtitle
    y -= 0.45 * inch
    sub_lines = wrap_text(c, subtitle, "Helvetica", 12, title_max_w)
    y = draw_centered_lines(c, sub_lines[:3], y, "Helvetica", 12, colors["text"], 16, front_cx)

    # Audience tag
    y -= 0.35 * inch
    tag = f"For {audience}" if audience else niche
    if tag:
        tag_w = min(c.stringWidth(tag, "Helvetica", 10) + 24, trim_w - 1.0 * inch)
        c.setFillColor(colors["secondary"])
        c.roundRect(front_cx - tag_w / 2, y - 4, tag_w, 22, 10, fill=1, stroke=0)
        c.setFillColor(colors["text"])
        c.setFont("Helvetica", 10)
        c.drawCentredString(front_cx, y + 2, tag)

    # Author bottom of front
    c.setFont("Helvetica", 12)
    c.setFillColor(colors["header_text"])
    c.drawCentredString(front_cx, content_bottom + 0.55 * inch, author)

    # Subtle line above author
    c.setStrokeColor(colors["line"])
    c.setLineWidth(0.6)
    c.line(front_cx - 1.2 * inch, content_bottom + 0.85 * inch, front_cx + 1.2 * inch, content_bottom + 0.85 * inch)

    # Optional: faint guide lines for trim (not printed meaningfully — help visual QA)
    # Uncomment for debug:
    # c.setStrokeColor(HexColor("#FF0000"))
    # c.setDash(3, 3)
    # c.rect(back_x, content_bottom, trim_w, trim_h, fill=0, stroke=1)
    # c.rect(front_x, content_bottom, trim_w, trim_h, fill=0, stroke=1)

    c.save()
    return {
        "success": True,
        "spineInches": round(dims["spine_inches"], 4),
        "fullWidthInches": round(dims["full_w_inches"], 4),
        "fullHeightInches": round(dims["full_h_inches"], 4),
        "pageCount": page_count,
        "spineTextIncluded": spine_ok and spine_w >= 0.25 * inch,
        "paperType": dims["paper"],
        "outputPath": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: generate_cover.py '<json_cfg>' <output_path>"}))
        sys.exit(1)
    cfg = json.loads(sys.argv[1])
    output_path = sys.argv[2]
    try:
        result = generate(cfg, output_path)
        print(json.dumps(result))
    except Exception as e:
        import traceback
        print(json.dumps({"error": str(e), "trace": traceback.format_exc()}))
        sys.exit(1)
