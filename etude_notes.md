# Etude Notes

## Purpose

Create a series of 32+ bar two-person duet etudes for MIDI Agent generation. Each bassist in `bass_rank.md` gets a bassist-anchored etude, paired with one or more guitarists from `etude_pairings.md`.

The bass part is for a 14-year-old beginner who should be pushed. The guitar part is for a 50-year-old ex-virtuoso who should also be pushed.

## Catalog Model

The catalog is organized as a collection per bassist. Each bass/guitar pairing is its own duet etude, not a blended multi-guitarist piece.

```text
Bassist Collection
  Guitarist Pairing
    Center Etude
    Peak Etude
```

Each bassist currently has 1-4 guitarist pairings. Because each bass/guitar pair gets two versions, each bassist can produce 2-8 etudes.

Current theoretical catalog size:

```text
182 bass/guitar pairings x 2 versions = 364 etudes
```

Practical production path:

1. Core center etudes: one strongest pairing per bassist.
2. Core peak etudes: peak version of each core pairing.
3. Strong alternate pairings.
4. Coverage pairings only when the musical/technical value remains clear.

## MIDI Agent Output Model

Each bass/guitar pair is one musical duet, but MIDI Agent should produce four synchronized tracks:

1. `Bass Performance`: audible electric bass part.
2. `Bass TAB`: matching bass fingering/TAB guide.
3. `Guitar Performance`: audible electric guitar part.
4. `Guitar TAB`: matching guitar fingering/TAB guide.

The performance and TAB tracks for each instrument must describe the same notes and rhythms. TAB tracks exist to preserve string/fret decisions for notation and practice; they should not introduce extra musical material.

MIDI Agent should not add drums, vocals, keys, backing tracks, percussion, or extra instruments. The result should remain a two-player practice duet even though the working file has four tracks.

## Source Vocabulary

Each etude should represent the source bassist's and guitarist's real style, not just a generic genre approximation. The writing should draw from real licks, exercises, and short excerpts that demonstrate the player's technical identity.

Construction order:

1. Study/exercise-derived excerpts.
2. Direct real excerpts where appropriate.
3. Original inspired connective material.

## Difficulty Model

Etudes should be graded from the source players' actual vocabulary. Do not normalize all pieces to the same difficulty.

Each etude should eventually support two versions:

- `center`: representative core repertoire of the source players.
- `peak`: challenge version aimed at the hardest vocabulary those players are known for.

## Pairing Principle

The pairing map is not a historical-collaboration list. A valid pairing requires style overlap and a strong technical conversation between bass and guitar. Era, scene, and historical collaboration are tie breakers after style and technique already fit.
