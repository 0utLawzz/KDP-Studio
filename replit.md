# KDP Digital Products Studio

An internal publishing tool for Nadeem (Bright Mindful Pages brand) to design, generate, and manage Amazon KDP low-content books — interiors, covers, listing metadata, and templates.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 8080 in dev, `$PORT` in production)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 20 (`.replit` module), TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `artifacts/kdp-studio/` — React/Vite frontend (port from `$PORT`, base path `/`)
- `artifacts/api-server/` — Express 5 API server (port 8080, paths `/api`)
- `artifacts/api-server/python/` — Python/reportlab generators for interiors, covers, listings
- `docs/` — public v2 specification and repository documentation
- `lib/db/` — Drizzle ORM schema + migrations (source of truth: `lib/db/src/schema/books.ts`)
- `lib/api-spec/openapi.yaml` — OpenAPI spec (source of truth for API contract)
- `lib/api-client-react/` — generated React Query hooks (run codegen to regenerate)
- `lib/api-zod/` — generated Zod schemas

## Architecture decisions

- API routes must be explicitly registered in `artifacts/api-server/src/routes/index.ts` — new route files are not auto-discovered.
- Python generators are called by the Express API via child_process; `reportlab` is installed by the root `postinstall` script.
- `DATABASE_URL` is runtime-managed by Replit — never set it manually.
- API client uses relative paths (e.g. `/api/stats`) — no base URL needed; Replit's path proxy routes `/api` to the API server.

## Product

- **Book Library** — create and manage KDP book projects (title, niche, trim size, palette, day count, etc.)
- **PDF Generation** — generate interior PDFs, full-wrap cover PDFs, and editable templates per book
- **Listing Generator** — produce KDP-ready title/subtitle/keyword/category metadata
- **Palettes** — browse built-in color palettes used in cover generation
- **Tasks** — internal task tracker for the publishing workflow
- **Public repository metadata** — README, security guidance, community templates, favicon, and social preview

## User preferences

- Work in small, independently verifiable stages; commit and push after each meaningful milestone.
- For visual work, show design directions first and wait for the user's choice before changing production generators.

## Gotchas

- **Python packages (reportlab, pillow)** are installed automatically via `postinstall` in `package.json` when `pnpm install` runs. The `pip` wrapper installs to `.pythonlibs/` (not the Nix store). Do not use `python3 -m pip` or `pip3` — use plain `pip` which routes through the Replit pip wrapper.
- If Python generation fails in production, verify `.pythonlibs/` is available and `pip install -r artifacts/api-server/python/requirements.txt` has run.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
