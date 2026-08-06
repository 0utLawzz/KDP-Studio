---
name: PDF icon rendering
description: Non-obvious ReportLab font behavior relevant to generated KDP interiors and covers.
---

When generating KDP PDFs with ReportLab, do not rely on Unicode decorative icons rendering correctly through the built-in Helvetica fonts. Use vector-drawn shapes or an explicitly embedded font with the required glyphs.

**Why:** The built-in PDF font fallback rendered otherwise valid Unicode symbols as solid squares in a production interior preview.

**How to apply:** Prefer simple vector icons for small decorative marks in generated interiors and covers; visually inspect at least one rendered page before checkpointing.