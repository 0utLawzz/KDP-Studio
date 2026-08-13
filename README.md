# KDP Studio

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Automation](https://img.shields.io/badge/Automation-Custom-blue)
![Status](https://img.shields.io/badge/Status-Active-success)

> A focused publishing workspace for planning, validating, generating, and organizing differentiated Bright Mindful Pages KDP planners, journals, and trackers.

## Topics / Keywords
`amazon-kdp` `kdp` `book-generation` `journals` `planners` `low-content-books` `print-on-demand` `publishing-tools` `reportlab` `typescript` `react` `vite` `postgresql` `automation` `custom-automation`

## What it does

- Organizes book projects, templates, palettes, and publishing tasks
- Validates KDP page-count and margin rules before generation
- Generates print-ready interior and full-wrap cover PDFs
- Produces KDP listing metadata and editable template packages
- Tracks whether a project is planned, generated, or manually published

The tool prepares files for KDP. It does **not** scrape Amazon or automate unofficial uploads.

## Run locally

```bash
pnpm install
pnpm --filter @workspace/api-server run dev
pnpm --filter @workspace/kdp-studio run dev
```

The app uses PostgreSQL via `DATABASE_URL`. Do not commit environment files or credentials.

## Project layout

- `artifacts/kdp-studio/` — React/Vite web app
- `artifacts/api-server/` — Express API and Python/reportlab generators
- `lib/db/` — Drizzle schema and database tooling
- `lib/api-spec/` — OpenAPI source contract
- `docs/` — public product specification and project documentation

## KDP guardrails

- 0.4 in safe margin on every interior page
- 72-page minimum for color interiors
- Spine text only at 79+ pages
- No copyrighted or scraped content
- No near-identical color-only variants

## Author
**Nadeem (OutLawZ)**  
Custom Automation Specialist  

📧 Contact: [net2outlawzz@gmail.com](mailto:net2outlawzz@gmail.com)  
🔗 GitHub: [0utLawzz](https://github.com/0utLawzz)

---

*Need custom KDP / publishing automation? Contact me.*

## License

MIT. See [`LICENSE`](LICENSE).
