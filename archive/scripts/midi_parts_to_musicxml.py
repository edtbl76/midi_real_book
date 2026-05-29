#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

from merge_midi_parts import MidiFile, parse_track, read_midi


PITCH_NAMES = [
    ("C", 0),
    ("C", 1),
    ("D", 0),
    ("D", 1),
    ("E", 0),
    ("F", 0),
    ("F", 1),
    ("G", 0),
    ("G", 1),
    ("A", 0),
    ("A", 1),
    ("B", 0),
]

GUITAR_TUNING = [(6, 40), (5, 45), (4, 50), (3, 55), (2, 59), (1, 64)]
BASS_TUNING = [(4, 26), (3, 33), (2, 38), (1, 43)]


@dataclass(frozen=True)
class MidiNote:
    start: int
    duration: int
    pitch: int
    velocity: int


@dataclass(frozen=True)
class ScoreEvent:
    start: int
    duration: int
    pitches: tuple[int, ...]


def midi_to_pitch(midi: int) -> tuple[str, int, int]:
    step, alter = PITCH_NAMES[midi % 12]
    return step, alter, midi // 12 - 1


def add_text(parent: ET.Element, tag: str, text: str | int) -> ET.Element:
    child = ET.SubElement(parent, tag)
    child.text = str(text)
    return child


def extract_notes(midi: MidiFile) -> list[MidiNote]:
    notes: list[MidiNote] = []
    active: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for track in midi.tracks:
        for event in parse_track(track):
            if not event.data:
                continue
            status = event.data[0]
            if not 0x80 <= status <= 0x9F:
                continue
            pitch = event.data[1]
            velocity = event.data[2]
            command = status & 0xF0
            if command == 0x90 and velocity > 0:
                active[pitch].append((event.tick, velocity))
            elif command == 0x80 or (command == 0x90 and velocity == 0):
                if active[pitch]:
                    start, start_velocity = active[pitch].pop(0)
                    if event.tick > start:
                        notes.append(MidiNote(start, event.tick - start, pitch, start_velocity))
    return sorted(notes, key=lambda note: (note.start, note.pitch))


def source_tempo(midi: MidiFile) -> int:
    for track in midi.tracks:
        for event in parse_track(track):
            if event.data[:2] == b"\xFF\x51" and len(event.data) >= 6:
                micros = int.from_bytes(event.data[-3:], "big")
                return round(60_000_000 / micros)
    return 120


def split_notes_to_events(notes: list[MidiNote], bar_ticks: int, total_bars: int) -> dict[int, list[ScoreEvent]]:
    by_measure: dict[int, list[MidiNote]] = defaultdict(list)
    for note in notes:
        remaining = note.duration
        cursor = note.start
        while remaining > 0:
            measure_index = cursor // bar_ticks
            if measure_index >= total_bars:
                break
            local_start = cursor % bar_ticks
            duration = min(remaining, bar_ticks - local_start)
            by_measure[measure_index].append(MidiNote(local_start, duration, note.pitch, note.velocity))
            cursor += duration
            remaining -= duration

    result: dict[int, list[ScoreEvent]] = {}
    for measure_index, measure_notes in by_measure.items():
        grouped: dict[tuple[int, int], list[int]] = defaultdict(list)
        for note in measure_notes:
            grouped[(note.start, note.duration)].append(note.pitch)
        result[measure_index] = [
            ScoreEvent(start, duration, tuple(sorted(pitches)))
            for (start, duration), pitches in sorted(grouped.items())
        ]
    return result


def duration_type(duration: int, divisions: int) -> tuple[str, int]:
    quarter = divisions
    mapping = {
        quarter * 4: ("whole", 0),
        quarter * 3: ("half", 1),
        quarter * 2: ("half", 0),
        quarter * 3 // 2: ("quarter", 1),
        quarter: ("quarter", 0),
        quarter * 3 // 4: ("eighth", 1),
        quarter // 2: ("eighth", 0),
        quarter // 4: ("16th", 0),
    }
    return mapping.get(duration, ("eighth", 0))


def string_fret_candidates(midi: int, instrument: str) -> list[tuple[int, int]]:
    tuning = BASS_TUNING if instrument == "bass" else GUITAR_TUNING
    max_fret = 17 if instrument == "bass" else 22
    return [(string, midi - open_pitch) for string, open_pitch in tuning if 0 <= midi - open_pitch <= max_fret]


def allocate_tab(pitches: tuple[int, ...], instrument: str) -> list[tuple[int, int]]:
    if not pitches:
        return []
    candidates = [string_fret_candidates(pitch, instrument) for pitch in pitches]
    if any(not choices for choices in candidates):
        return [(1, 0) for _ in pitches]
    best: tuple[int, list[tuple[int, int]]] | None = None

    def cost(positions: list[tuple[int, int]]) -> int:
        strings = [string for string, _ in positions]
        frets = [fret for _, fret in positions]
        if len(set(strings)) != len(strings):
            return 10_000
        fret_span = max(frets) - min(frets)
        average_fret = sum(frets) / len(frets)
        position_cost = abs(average_fret - (5 if instrument == "bass" else 7))
        return round(fret_span * 5 + position_cost * 2 + max(frets))

    def search(index: int, chosen: list[tuple[int, int]]) -> None:
        nonlocal best
        if index == len(candidates):
            current_cost = cost(chosen)
            if best is None or current_cost < best[0]:
                best = (current_cost, chosen[:])
            return
        for position in candidates[index]:
            search(index + 1, chosen + [position])

    search(0, [])
    return best[1] if best else [choices[0] for choices in candidates]


def add_staff_tuning(parent: ET.Element, instrument: str) -> None:
    tuning = BASS_TUNING if instrument == "bass" else GUITAR_TUNING
    for line, (_, midi) in enumerate(tuning, start=1):
        staff_tuning = ET.SubElement(parent, "staff-tuning", line=str(line))
        step, alter, octave = midi_to_pitch(midi)
        add_text(staff_tuning, "tuning-step", step)
        if alter:
            add_text(staff_tuning, "tuning-alter", alter)
        add_text(staff_tuning, "tuning-octave", octave)


def add_attributes(measure: ET.Element, divisions: int, *, tab: bool, instrument: str) -> None:
    attrs = ET.SubElement(measure, "attributes")
    add_text(attrs, "divisions", divisions)
    key = ET.SubElement(attrs, "key")
    add_text(key, "fifths", 0)
    time = ET.SubElement(attrs, "time")
    add_text(time, "beats", 4)
    add_text(time, "beat-type", 4)
    clef = ET.SubElement(attrs, "clef")
    if tab:
        add_text(clef, "sign", "TAB")
        staff = ET.SubElement(attrs, "staff-details")
        add_text(staff, "staff-lines", 4 if instrument == "bass" else 6)
        add_staff_tuning(staff, instrument)
    else:
        add_text(clef, "sign", "F" if instrument == "bass" else "G")
        add_text(clef, "line", 4 if instrument == "bass" else 2)


def add_direction(measure: ET.Element, tempo: int) -> None:
    direction = ET.SubElement(measure, "direction", placement="above")
    dtyp = ET.SubElement(direction, "direction-type")
    met = ET.SubElement(dtyp, "metronome")
    add_text(met, "beat-unit", "quarter")
    add_text(met, "per-minute", tempo)
    sound = ET.SubElement(direction, "sound")
    sound.set("tempo", str(tempo))


def add_note(
    measure: ET.Element,
    duration: int,
    pitch: int | None,
    divisions: int,
    *,
    chord: bool = False,
    tab_position: tuple[int, int] | None = None,
) -> None:
    note = ET.SubElement(measure, "note")
    if chord:
        ET.SubElement(note, "chord")
    if pitch is None:
        ET.SubElement(note, "rest")
    else:
        p = ET.SubElement(note, "pitch")
        step, alter, octave = midi_to_pitch(pitch)
        add_text(p, "step", step)
        if alter:
            add_text(p, "alter", alter)
        add_text(p, "octave", octave)
    add_text(note, "duration", duration)
    add_text(note, "voice", 1)
    note_type, dots = duration_type(duration, divisions)
    add_text(note, "type", note_type)
    for _ in range(dots):
        ET.SubElement(note, "dot")
    if tab_position is not None:
        notations = ET.SubElement(note, "notations")
        technical = ET.SubElement(notations, "technical")
        add_text(technical, "string", tab_position[0])
        add_text(technical, "fret", tab_position[1])


def write_part(
    score: ET.Element,
    part_id: str,
    events_by_measure: dict[int, list[ScoreEvent]],
    *,
    total_bars: int,
    divisions: int,
    tempo: int,
    tab: bool,
    instrument: str,
) -> None:
    part = ET.SubElement(score, "part", id=part_id)
    bar_ticks = divisions * 4
    for measure_number in range(1, total_bars + 1):
        measure = ET.SubElement(part, "measure", number=str(measure_number))
        if measure_number == 1:
            add_attributes(measure, divisions, tab=tab, instrument=instrument)
            add_direction(measure, tempo)
        cursor = 0
        for event in events_by_measure.get(measure_number - 1, []):
            if event.start > cursor:
                add_note(measure, event.start - cursor, None, divisions)
            positions = allocate_tab(event.pitches, instrument) if tab else [None] * len(event.pitches)
            for index, pitch in enumerate(event.pitches):
                add_note(
                    measure,
                    event.duration,
                    pitch,
                    divisions,
                    chord=index > 0,
                    tab_position=positions[index] if tab else None,
                )
            cursor = event.start + event.duration
        if cursor < bar_ticks:
            add_note(measure, bar_ticks - cursor, None, divisions)


def build_score(directory: Path) -> ET.Element:
    guitar = read_midi(directory / "Electric Guitar.mid")
    bass = read_midi(directory / "Electric Bass.mid")
    if guitar.division != bass.division:
        raise ValueError("Guitar and bass MIDI files use different PPQ divisions")

    divisions = guitar.division
    guitar_notes = extract_notes(guitar)
    bass_notes = extract_notes(bass)
    max_tick = max(
        [note.start + note.duration for note in guitar_notes + bass_notes],
        default=divisions * 4,
    )
    total_bars = max(1, (max_tick + divisions * 4 - 1) // (divisions * 4))
    tempo = source_tempo(guitar)
    guitar_events = split_notes_to_events(guitar_notes, divisions * 4, total_bars)
    bass_events = split_notes_to_events(bass_notes, divisions * 4, total_bars)

    score = ET.Element("score-partwise", version="4.0")
    work = ET.SubElement(score, "work")
    add_text(work, "work-title", directory.name)
    part_list = ET.SubElement(score, "part-list")
    for part_id, name in [
        ("P1", "Electric Guitar"),
        ("P2", "Electric Guitar Tablature"),
        ("P3", "Electric Bass"),
        ("P4", "Electric Bass Tablature"),
    ]:
        score_part = ET.SubElement(part_list, "score-part", id=part_id)
        add_text(score_part, "part-name", name)

    write_part(score, "P1", guitar_events, total_bars=total_bars, divisions=divisions, tempo=tempo, tab=False, instrument="guitar")
    write_part(score, "P2", guitar_events, total_bars=total_bars, divisions=divisions, tempo=tempo, tab=True, instrument="guitar")
    write_part(score, "P3", bass_events, total_bars=total_bars, divisions=divisions, tempo=tempo, tab=False, instrument="bass")
    write_part(score, "P4", bass_events, total_bars=total_bars, divisions=divisions, tempo=tempo, tab=True, instrument="bass")
    return score


def pretty_xml(root: ET.Element) -> str:
    raw = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(raw).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    doctype = '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">'
    return pretty.replace("<score-partwise", doctype + "\n<score-partwise", 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create four-part notation/TAB MusicXML from guitar and bass MIDI files.")
    parser.add_argument("directory", type=Path, help="Directory containing Electric Guitar.mid and Electric Bass.mid")
    parser.add_argument("--output", type=Path, help="Output MusicXML path")
    args = parser.parse_args()
    output = args.output or args.directory / f"{args.directory.name}.musicxml"
    output.write_text(pretty_xml(build_score(args.directory)), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
