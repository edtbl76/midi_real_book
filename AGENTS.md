# Repository Guidelines

## Project Structure & Module Organization

Only three files are authoritative for current work:

- `guitar_ranks.md`: ranked guitarist list split into `Virtuosos` and `Everyone Else`, with technical rationale and styles.
- `bass_rank.md`: ranked bassist list using the same tier concept, with ranking basis stated at the top.
- `etude_pairings.md`: bassist-anchored pairing workspace. Each row assigns up to four guitarists and a style cluster; summary counts and frequency sections should reflect completed pairings.

Treat all other files as stale or irrelevant unless the user explicitly says otherwise.

## Build, Test, and Development Commands

There is no build system, package manifest, or runnable test suite for the relevant corpus. Use text inspection commands while editing:

- `sed -n '1,120p' guitar_ranks.md`: review ranking format and tier boundaries.
- `sed -n '1,120p' bass_rank.md`: review bassist ranking criteria and table shape.
- `sed -n '1,180p' etude_pairings.md`: review pairing rows and summary sections.
- `rg "Name" *.md`: find whether a musician already appears before adding or reusing them.

## Coding Style & Naming Conventions

Keep Markdown tables stable and easy to diff. Preserve existing column names, rank numbering, capitalization, and tier headings. Use `—` for intentionally empty pairing cells in `etude_pairings.md`. Style clusters should be short slash-separated phrases, for example `jazz fusion / funk` or `progressive metal`.

When adding rationale text, keep it concise and evidence-oriented: focus on technique, harmonic/rhythmic sophistication, idiomatic fit, stylistic range, or documented session/band vocabulary. Avoid unsupported superlatives.

## Testing Guidelines

Validate edits manually. After changing ranks, check numbering remains sequential within the affected table. After filling pairings, update `Total pairings`, `Guitarists used`, `Guitarists unused`, the `Guitarist Frequency Chart`, and `Unused Guitarists` if those sections are part of the change. Cross-check guitarist names against `guitar_ranks.md` and bassist names against `bass_rank.md`.

## Commit & Pull Request Guidelines

There is no meaningful commit history to infer conventions from. Use concise imperative commit messages, such as `Fill fusion bassist pairings` or `Adjust guitarist virtuoso ranks`. Pull requests should summarize changed rankings or pairings, explain notable judgment calls, and mention any count/table consistency checks performed.

## Agent-Specific Instructions

Do not base decisions on stale generated prompts, scripts, README content, or project metadata. For pairing work, prioritize idiomatic excellence over genre adjacency: a guitarist should fit the bassist’s vocabulary, era, technical level, and likely musical conversation.
