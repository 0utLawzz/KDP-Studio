# KDP Digital Products Studio

KDP Digital Products Studio is a single-user publishing workspace for **Bright Mindful Pages**. It helps plan, validate, generate, and organize original low-content and medium-content paperback products such as planners, journals, and trackers.

## What it does

- Organizes book projects, templates, palettes, and publishing tasks
- Validates KDP page-count and margin rules before generation
- Generates print-ready interior and full-wrap cover PDFs
- Produces KDP listing metadata and editable template packages
- Tracks whether a project is planned, generated, or manually published

The tool prepares files for KDP. It does not scrape Amazon or automate unofficial uploads.

## Run locally

```bash
pnpm install
pnpm --filter @workspace/api-server run dev
pnpm --filter @workspace/kdp-studio run dev
```

The app uses the Replit-managed PostgreSQL database through `DATABASE_URL`. Do not commit environment files or credentials.

## Project layout

- `artifacts/kdp-studio/` — React/Vite web app
- `artifacts/api-server/` — Express API and Python/reportlab generators
- `lib/db/` — Drizzle schema and database tooling
- `lib/api-spec/` — OpenAPI source contract
- `docs/` — public product specification and project documentation
- `.agents/skills/kdp-book-studio/` — concise KDP operating rules

## KDP guardrails

- 0.4 in safe margin on every interior page
- 72-page minimum for color interiors
- Spine text only at 79+ pages
- No copyrighted or scraped content
- No near-identical color-only variants
- Subtitles use one core value proposition instead of keyword stuffing

See [`docs/KDP-Digital-Products-Studio-V2-Master-Build-Specification.md`](docs/KDP-Digital-Products-Studio-V2-Master-Build-Specification.md) for the full v2 plan.

## License

MIT. See [`LICENSE`](LICENSE).