#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re


BASE_PROMPT = """Create a 32-bar instrumental etude for electric bass and electric guitar.

Output should be MIDI-first and suitable for later notation, TAB extraction, or DAW refinement.

Tracks:
1. Electric Bass only
2. Electric Guitar only

Do not include drums, vocals, keys, synths, percussion, backing tracks, or extra instruments.

Difficulty:
- Bass: intermediate. Playable and idiomatic, but not simplified into generic roots.
- Guitar: advanced/pro rock/fusion level. The guitar should be the featured technical voice while still sounding musical and playable.

Composition requirements:
- Original music only. Do not quote or closely imitate any existing song.
- It should sound like a complete short etude, not a loop or riff fragment.
- Approximately 32 bars.
- Clear A/B form, such as 8-bar A, 8-bar A variation, 8-bar B, 8-bar final return/development.
- Strong recurring motif.
- Variation and development across sections.
- Tasteful fills at phrase endings.
- Bass and guitar should interact musically through call/response, rhythmic locking, contrast, or counterlines.
- Keep both parts clean enough that they can later be transcribed into standard notation and TAB.
- Start from the bass part: write a real bassline that feels like an intermediate exercise, riff, lick, groove, or étude inspired by the named bassist and style. It should have idiomatic articulation, position logic, recurring shapes, phrase-ending fills, and enough variation to be useful as a practice study.
- Build the guitar part on top of that bassline: write a professional/advanced guitar etude idiomatic to the named guitarist(s) and style. It should feel informed by real exercises, riffs, solos, comping patterns, and lead/rhythm vocabulary associated with the guitarist(s), while remaining fully original.
- Guitar should not be simple accompaniment. Include idiomatic lead/rhythm hybrid writing, developed riffs, melodic lead answers, double-stops or chord fragments, and one or two technically impressive moments per section.
- Use advanced guitar vocabulary appropriate to the named guitarist(s): alternate-picked sequences, legato runs, string-skipping, hybrid picking, sweep-picked arpeggio fragments, tapped ornaments, harmonics, wide bends, expressive vibrato, odd groupings, rhythmic comping cells, or fast position shifts where stylistically appropriate.
- Keep the guitar part performance-grade: challenging enough for an advanced player, but not nonstop shredding. Preserve clear motifs, phrasing, breathing room, and a strong groove.
- Avoid impossible guitar voicings, incoherent fretboard jumps, excessive unmusical note density, and unplayable bass fills.
- Use idiomatic articulations where musically appropriate: palm muting, staccato, accents, slides, bends, muted notes, legato, or harmonics-like effects.
- Prioritize feel, groove, melody, and performance value over complexity.

Style target:
{style_target}

Generate a complete two-track MIDI composition that sounds musical and performance-ready.
"""


def slugify(text: str) -> str:
    text = text.lower().replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_rows(plan: Path) -> list[tuple[str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str]] = []
    for line in plan.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("|---") or "Etude Concept" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) in {5, 6}:
            cells = cells[1:]
        if len(cells) == 4:
            cells.insert(3, "")
        if len(cells) != 5:
            raise ValueError(f"Unexpected table row: {line}")
        rows.append((cells[0], cells[1], cells[2], cells[3], cells[4]))
    return rows


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    prompts_dir = root / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    rows = parse_rows(root / "etude-plan.md")

    index_lines = [
        "# MIDI Agent Prompts",
        "",
        "One full copy/paste prompt per etude.",
        "",
    ]

    for number, (concept, bass_player, guitar_players, band_influence, description) in enumerate(rows, start=1):
        slug = slugify(concept)
        filename = f"{number:02d}-{slug}.md"
        style_target = (
            f"{concept}. Bass player influence: {bass_player}. "
            f"Guitar player influence: {guitar_players}. {description}"
        )
        body = f"# {concept}\n\n```text\n{BASE_PROMPT.format(style_target=style_target)}```\n"
        (prompts_dir / filename).write_text(body, encoding="utf-8")
        index_lines.append(f"- [{concept}]({filename})")

    (prompts_dir / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} prompt files to {prompts_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
