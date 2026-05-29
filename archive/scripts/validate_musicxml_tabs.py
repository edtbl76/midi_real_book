#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET


PITCH_CLASS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
TUNINGS = {
    "P2": {6: 40, 5: 45, 4: 50, 3: 55, 2: 59, 1: 64},
    "P4": {4: 26, 3: 33, 2: 38, 1: 43},
}


def midi_pitch(note: ET.Element) -> int | None:
    pitch = note.find("pitch")
    if pitch is None:
        return None
    step = pitch.findtext("step")
    octave = pitch.findtext("octave")
    if step is None or octave is None:
        return None
    alter = int(pitch.findtext("alter", "0"))
    return (int(octave) + 1) * 12 + PITCH_CLASS[step] + alter


def tab_position(note: ET.Element) -> tuple[int, int] | None:
    technical = note.find("notations/technical")
    if technical is None:
        return None
    string = technical.findtext("string")
    fret = technical.findtext("fret")
    if string is None or fret is None:
        return None
    return int(string), int(fret)


def validate(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    errors: list[str] = []
    for part in root.findall("part"):
        part_id = part.attrib["id"]
        if part_id not in TUNINGS:
            continue
        tuning = TUNINGS[part_id]
        for measure in part.findall("measure"):
            chord_strings: set[int] = set()
            measure_number = measure.attrib.get("number", "?")
            for note in measure.findall("note"):
                if note.find("chord") is None:
                    chord_strings.clear()
                pitch = midi_pitch(note)
                if pitch is None:
                    continue
                position = tab_position(note)
                if position is None:
                    errors.append(f"{part_id} m.{measure_number}: missing TAB position")
                    continue
                string, fret = position
                if string in chord_strings:
                    errors.append(f"{part_id} m.{measure_number}: duplicate string {string} in chord")
                chord_strings.add(string)
                if tuning.get(string, -999) + fret != pitch:
                    errors.append(f"{part_id} m.{measure_number}: string {string} fret {fret} does not match pitch {pitch}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("musicxml", type=Path)
    args = parser.parse_args()
    errors = validate(args.musicxml)
    if errors:
        print("TAB validation failed")
        for error in errors[:100]:
            print(f"- {error}")
        if len(errors) > 100:
            print(f"- ... {len(errors) - 100} more")
        return 1
    print("TAB validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
