---
name: kdp-book-studio
description: Use for Bright Mindful Pages KDP planners, journals, trackers, covers, listings, generators, and the KDP Digital Products Studio.
---

# KDP Book Studio

This is the project-specific operating brief for Bright Mindful Pages and the KDP Digital Products Studio. The full product plan is `docs/KDP-Digital-Products-Studio-V2-Master-Build-Specification.md`.

## Product boundaries

- Build low-content books or genuinely original medium-content books only.
- Never scrape, copy, or present generated material as authoritative facts.
- Never mass-produce near-identical books with only a color swap. Variants must differ by audience, structure, depth, or format.
- This is a single-user internal tool. Do not add accounts or unofficial KDP upload automation without explicit approval.
- UI copy must be plain-language and useful to a non-developer.

## Fixed KDP rules

- Supported trims: 6×9 in (default), 5×8 in, and 8.5×11 in.
- Use the shared palette catalog; do not invent ad-hoc colors.
- Keep all interior content at least 0.4 in from every page edge. Decorative backgrounds are inset, never edge-to-edge.
- Enforce margin safety with reusable validation before exporting; fail loudly when invalid.
- Color interiors require at least 72 pages. Pad short books before export.
- Spine text is allowed only at 79+ pages; recalculate cover dimensions whenever page count changes.
- Use Paperback, verify current KDP categories, and disclose AI-generated text/images when applicable.
- Subtitles state one core value proposition. Put feature lists in the description, not the subtitle or cover.
- Produce an interior PDF, exact-page-count cover PDF, KDP listing metadata, and a progress entry for each generated book.

## Publishing checklist

- [ ] Interior has at least 72 color pages and passes margin validation.
- [ ] Cover dimensions match the final page count and trim.
- [ ] Subtitle is not keyword-stuffed; description contains the feature detail.
- [ ] Seven lowercase keywords and 2–3 verified KDP categories are ready.
- [ ] Paperback, ISBN, large-print, and AI disclosure settings are confirmed.
- [ ] Price is checked against live competitors; Print Previewer is approved manually.