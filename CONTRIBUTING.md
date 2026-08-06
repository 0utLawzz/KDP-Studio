# Contributing

Thanks for helping improve KDP Digital Products Studio.

## Before opening a change

1. Read the v2 specification in `docs/`.
2. Follow the KDP rules in `.agents/skills/kdp-book-studio/SKILL.md`.
3. Keep generated content original and structurally differentiated.
4. Never add credentials, private publishing source files, or uploaded customer material.

## Checks

Run the checks that match your change:

```bash
pnpm run typecheck
pnpm run build
```

For generator changes, also verify page count, safe margins, cover dimensions, and the generated output package.

## Commit style

Use short messages in this format:

```text
feat: add a publishing workflow
fix: prevent unsafe page export
docs: clarify KDP checklist
refactor: share palette definitions
```