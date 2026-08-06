# KDP Low-Content Book — Reusable Guideline
### (Bright Mindful Pages — Planner/Journal Series)

Is guideline ko naye chat mein paste kar dena jab bhi related book (naya topic, naya version, ya isi niche ka extension) banana ho. Sirf **[CHANGE THIS]** wale hisse update karne hain, baaki process same rehta hai.

---

## 1. Book Concept

| Field | Current Example | [CHANGE THIS] |
|---|---|---|
| Niche/Topic | ADHD Daily Planner | Naya topic (e.g. Anxiety Journal, Sobriety Tracker) |
| Format | Daily planner, 60-day undated | Journal / tracker / coloring / hybrid |
| Target Buyer | Adults with ADHD | Naya target audience |
| Brand/Author Name | Bright Mindful Pages | Same rakhna hai (consistent brand) ya naya |

---

## 2. Design System (reuse as-is)

**Color Palette:**
- Lavender: `#E6D9F7`
- Mint: `#D6F3E8`
- Peach: `#FFE3D1`
- Pink: `#FBD6E3`
- Sky Blue: `#D9EEFB`
- Text (dark plum): `#4A3F55`

**Fonts:** Helvetica-Bold (headings), Helvetica (body) — reportlab standard fonts, ya Canva mein "Fredoka"/"Baloo 2" (rounded, friendly)

---

## 3. Interior Generation (Python + reportlab)

**Critical technical rules learned (follow every time):**

1. **Trim size:** 6x9 in default (confirm with user)
2. **Margins:** MARGIN = 0.4in on all sides — **NEVER let any rect/circle/text touch x=0, y=0, PAGE_W, or PAGE_H.** Full-width/edge-to-edge color banners are the #1 cause of KDP margin rejection under "No Bleed."
3. **All decorative banners/backgrounds must be INSET within the margin box**, not edge-to-edge — use `rounded(c, MARGIN, ..., PAGE_W - 2*MARGIN, ...)` pattern, never `rounded(c, 0, ..., PAGE_W, ...)`.
4. **Bottom margin buffer:** always simulate/verify (via quick Python calc) that the lowest element (last note line, footer, etc.) sits at least 0.05–0.1in above the bottom MARGIN before generating the full file.
5. **Minimum page count for Standard/Premium Color interior = 72 pages.** Plan day-count accordingly (e.g., 60-day + front matter + weekly reviews = ~73 pages). Black & White interior has a lower minimum — check current KDP rule if switching ink type.
6. **Spine text only allowed at 79+ pages** (KDP Cover Creator requires 80+). Below that, spine = color fill only, no text.
7. Avoid tiny graphic objects positioned exactly at MARGIN (e.g. circles) — offset by their radius so they don't clip past the margin line by even 1pt.
8. No page footer/page-number unless it's confirmed to sit within the margin box.

**Reuse the existing script structure:** title_page → intro_page ("How to Use") → habit_tracker_page(s) → daily_page (loop) → weekly_review_page (every 7 days) → pad with blank_notes_page if under 72-page minimum.

---

## 4. KDP Listing Template

| Field | Value | [CHANGE THIS] |
|---|---|---|
| Format | Paperback (NOT Kindle eBook — fillable content doesn't work on eBook) | Confirm same logic applies |
| Author/Publisher | Bright Mindful Pages | Keep, unless new sub-brand |
| Title | [Topic] + format word (e.g. "Daily Planner", "Journal") | New |
| Subtitle | "A [N]-Day Undated Planner with [feature 1], [feature 2] & [feature 3] for [outcome]" | New |
| Trim Size | 6x9 in | Confirm |
| Interior Type | Full Color / Standard Color (if colorful) or B&W (if minimal) | Confirm |
| Low-content book checkbox | Yes | Keep |
| Large-print checkbox | No (unless body text ≥16pt) | Confirm |
| ISBN | Publish without ISBN (free KDP option) | Keep |
| Price | Research competitor pricing first, then set | New |
| Royalty | 60% | Keep |
| AI-generated content disclosure | Yes (images/layout) | Keep |

**Categories:** Pick 2–3 from KDP's *actual* dropdown (not generic guesses) — navigate the real category tree in KDP dashboard, don't assume options exist. Look for the closest real match to: format (Time Management/Self-Management/Journaling) + condition/topic (Mental Health > General, or relevant subcategory).

**Keywords (7):** Format = `[condition/topic] planner for adults`, `daily planner for [topic]`, `undated planner [topic]`, `[core feature] journal`, `[feature] tracker`, `[format] planner`, `[audience] planner`.

---

## 5. Cover Brief Template (Canva)

1. Get exact dimensions from **KDP Cover Calculator** (https://kdp.amazon.com/cover-calculator) using: binding=Paperback, interior type, paper type, trim size, **final page count** — never guess.
2. Front cover: Title (bold rounded font) + subtitle + 2–3 relevant icons + brand name
3. Back cover: "What's Inside" bullet list (4–5 features) + barcode white space (bottom-right, 0.25x0.25in margin) + brand name/tagline
4. Spine: color fill only if <79 pages; add text only if 79+ pages
5. Export: PDF Print format, delete all guide/template layers before final export

---

## 6. Pre-Upload Checklist

- [ ] Interior PDF: page count ≥ 72 (color) confirmed
- [ ] Interior PDF: no element touches page edge (margin-safe)
- [ ] Cover PDF: matches Cover Calculator's exact dimensions
- [ ] Subtitle/description page-count references match actual interior
- [ ] Categories selected from real KDP dropdown (screenshot-verified)
- [ ] AI content disclosure = Yes
- [ ] Price set after competitor research
- [ ] Upload → Print Previewer → check for margin/font errors → Approve

---

## 7. Common Errors & Fixes (from experience)

| Error | Cause | Fix |
|---|---|---|
| "Interior must have minimum X pages" | Page count below KDP's ink-type minimum | Add days/content or padding pages |
| "Text/object outside margins" | Edge-to-edge color banner or element positioned exactly at margin | Inset all backgrounds by MARGIN; verify with Python calc before generating |
| "Fonts not properly embedded" | Standard fonts not auto-embedded | Informational only — KDP embeds automatically, not blocking |
| Spine text rejected | Book under 79 pages | Remove spine text, color fill only |
