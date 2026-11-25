# AGENTS.md

## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/<feature-slug>/` in this repo. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context layout: one `GLOSSARY.md` at the repo root plus `docs/adr/`. See `docs/agents/domain.md`.

## Git workflow for tickets

- Never commit directly to `main`. Each ticket is implemented on its own branch `ticket/NN-<slug>`, created from the current `main`.
- `/implement` commits go to the ticket branch only; review compares with `git diff main...HEAD`.
- Merging to `main` happens via PR (or explicit user instruction), after review and green CI.
