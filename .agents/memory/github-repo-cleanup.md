---
name: Public repository cleanup
description: Keep imported private material out of public GitHub repositories while preserving canonical project guidance.
---

Imported Replit projects may contain sensitive files under `attached_assets/` and large root archives. Preserve only explicitly canonical documents in public locations such as `docs/`, keep the project-specific skill concise, and remove the import-only directory plus archives from the tracked tree. GitHub API metadata updates can succeed even when the Replit GitHub push helper is blocked by an identity mismatch; a token-authenticated Git push may still work.

**Why:** Public repositories can expose uploaded generator source, publishing notes, images, or other trade-secret material even when the application itself does not reference them.

**How to apply:** Before publishing an imported repo, inspect tracked paths, preserve only the requested specification/skill, add secret/archive ignores, scan for stale asset references, and verify both GitHub metadata and the pushed branch.