# Agentic-Driven Development Workflow

Notes on the skill system set up in this repo (from Matt Pocock's `mattpocock/skills`, MIT).
Skills are plain `SKILL.md` files — no platform lock-in. Installed user-global at
`~/.agents/skills/` so they work in every project.

## How skills work in Vibe

- A skill = one directory with a `SKILL.md` (YAML frontmatter + markdown body), e.g.
  `~/.agents/skills/grill-with-docs/SKILL.md`.
- Discovery order (first match wins): `skill_paths` → project `.vibe/skills/` →
  project `.agents/skills/` (both need a trusted folder) → `~/.vibe/skills/` →
  `~/.agents/skills/`.
- Frontmatter: `name` (slug, matches dir), `description` (the only text the model sees
  before loading — the routing text), `user-invocable` (default true → `/name` in the
  slash menu), `disable-model-invocation: true` (hidden from the model; only the user
  can trigger it via `/name`).
- A "front door" skill (e.g. `/grill-with-docs`) delegates by prose: its body says
  `Call the Skill tool with "grilling"`. The model then emits `skill({name})` calls and
  the harness injects the referenced SKILL.md into context. No imports, no code.

## Installed skill set (dependency closure verified)

```
~/.agents/skills/
├── grill-me / grill-with-docs   ← front doors (disable-model-invocation: true)
├── grilling / domain-modeling   ← primitives (interview loop / glossary+ADR discipline)
├── to-spec / to-tickets         ← spec & ticket front doors
├── implement / tdd / code-review
├── codebase-design              ← reference tdd consults
├── retro / writing-for-agents   ← self-improvement loop
└── setup-matt-pocock-skills     ← run once per repo
```

## The flow

```
/grill-with-docs → /to-spec → /to-tickets → /implement <ticket> → /code-review → /retro
```

1. **`/grill-with-docs`** (in a repo, at the start of a change): interviews you in
   rounds (each round = the whole "frontier" of questions whose prerequisites are
   settled). Writes resolved terms to `GLOSSARY.md` inline, term by term; decisions that
   are hard to reverse + surprising + a real trade-off become ADRs in `docs/adr/`.
   Everything else lives only in the conversation — hand it to `/to-spec` in the same
   session. `/grill-me` is the same interview, stateless, no repo, no files.
2. **`/to-spec`**: synthesizes the conversation into a spec published to the tracker.
   No re-interviewing.
3. **`/to-tickets`**: splits the spec into tracer-bullet tickets (each a narrow but
   complete vertical slice) with blocking edges, published to the tracker.
4. **`/implement <ticket>`**: fetches the ticket, builds test-first (delegates to
   `tdd`), typechecks/tests progressively, then calls `code-review`.
5. **`/code-review`**: two-axis review of the diff (repo standards + spec fidelity) via
   parallel subagents.
6. **`/retro`**: reads session logs and proposes improvements to the agent environment
   itself (skills, AGENTS.md, GLOSSARY.md, docs) — the native self-improvement loop.

## Per-repo setup

- Trust the folder once (persisted in `~/.vibe/trusted_folders.toml`).
- Run `/setup-matt-pocock-skills` once per repo: chooses the issue tracker (GitHub
  Issues via Vibe's connector — free; or local markdown files, zero setup) and your
  triage label vocabulary. `to-spec`/`to-tickets` read this config. Local files =
  one md file per ticket, edges as text; GitHub = issues with native "blocked by"
  links and labels.

## Gotchas

- Partial loading: if a delegated skill isn't installed, the interview runs but no
  GLOSSARY.md/ADRs appear (or questions dump at once). After a grill, verify the files.
- GLOSSARY.md is vocabulary only — not a spec. Most decisions don't earn an ADR.
- Downstream skills read `GLOSSARY.md` (to-tickets, tdd) so names use the domain words;
  `domain-modeling` challenges words that conflict with it.
