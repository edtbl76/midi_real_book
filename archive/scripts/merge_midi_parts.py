#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass
class MidiFile:
    fmt: int
    division: int
    tracks: list[bytes]


@dataclass
class Event:
    tick: int
    data: bytes
    order: int


CHANNEL_EVENT_LENGTHS = {
    0x8: 2,
    0x9: 2,
    0xA: 2,
    0xB: 2,
    0xC: 1,
    0xD: 1,
    0xE: 2,
}


def read_varlen(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    while True:
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, offset


def write_varlen(value: int) -> bytes:
    buffer = value & 0x7F
    value >>= 7
    while value:
        buffer <<= 8
        buffer |= ((value & 0x7F) | 0x80)
        value >>= 7
    out = bytearray()
    while True:
        out.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            return bytes(out)


def read_midi(path: Path) -> MidiFile:
    data = path.read_bytes()
    if data[:4] != b"MThd":
        raise ValueError(f"{path} is not a standard MIDI file")
    header_len = struct.unpack(">I", data[4:8])[0]
    fmt, ntrks, division = struct.unpack(">HHH", data[8:14])
    offset = 8 + header_len
    tracks = []
    for _ in range(ntrks):
        if data[offset : offset + 4] != b"MTrk":
            raise ValueError(f"{path} has an invalid track chunk")
        length = struct.unpack(">I", data[offset + 4 : offset + 8])[0]
        offset += 8
        tracks.append(data[offset : offset + length])
        offset += length
    return MidiFile(fmt, division, tracks)


def parse_track(track: bytes) -> list[Event]:
    offset = 0
    tick = 0
    running_status: int | None = None
    order = 0
    events: list[Event] = []

    while offset < len(track):
        delta, offset = read_varlen(track, offset)
        tick += delta
        status = track[offset]

        if status < 0x80:
            if running_status is None:
                raise ValueError("Running status encountered without previous status")
            status = running_status
            data_start = offset
        else:
            offset += 1
            data_start = offset
            if status < 0xF0:
                running_status = status

        if status == 0xFF:
            meta_type = track[offset]
            offset += 1
            length, offset = read_varlen(track, offset)
            payload = track[offset : offset + length]
            offset += length
            events.append(Event(tick, bytes([0xFF, meta_type]) + write_varlen(length) + payload, order))
        elif status in (0xF0, 0xF7):
            length, offset = read_varlen(track, offset)
            payload = track[offset : offset + length]
            offset += length
            events.append(Event(tick, bytes([status]) + write_varlen(length) + payload, order))
        else:
            high = status >> 4
            length = CHANNEL_EVENT_LENGTHS[high]
            payload = track[data_start : data_start + length]
            offset = data_start + length
            events.append(Event(tick, bytes([status]) + payload, order))
        order += 1
    return events


def retarget_channel(event: Event, channel: int) -> Event | None:
    status = event.data[0]
    if status == 0xFF and event.data[1] == 0x2F:
        return None
    if status == 0xFF and event.data[1] == 0x03:
        return None
    if 0x80 <= status <= 0xEF:
        status = (status & 0xF0) | channel
        if status >> 4 == 0xC:
            return None
        return Event(event.tick, bytes([status]) + event.data[1:], event.order)
    return event


def make_meta_track(source_track: bytes, name: str) -> bytes:
    events = [
        Event(0, b"\xFF\x03" + write_varlen(len(name.encode("utf-8"))) + name.encode("utf-8"), -1)
    ]
    for event in parse_track(source_track):
        if event.data[:2] == b"\xFF\x2F":
            continue
        if event.data[0] == 0xFF and event.data[1] in {0x03}:
            continue
        if event.data[0] == 0xFF:
            events.append(event)
    return build_track(events)


def make_part_track(source_track: bytes, name: str, channel: int, program: int) -> bytes:
    name_bytes = name.encode("utf-8")
    events = [
        Event(0, b"\xFF\x03" + write_varlen(len(name_bytes)) + name_bytes, -2),
        Event(0, bytes([0xC0 | channel, program]), -1),
    ]
    for event in parse_track(source_track):
        retargeted = retarget_channel(event, channel)
        if retargeted is not None:
            events.append(retargeted)
    return build_track(events)


def build_track(events: list[Event]) -> bytes:
    events = sorted(events, key=lambda event: (event.tick, event.order))
    body = bytearray()
    previous_tick = 0
    for event in events:
        body.extend(write_varlen(event.tick - previous_tick))
        body.extend(event.data)
        previous_tick = event.tick
    body.extend(b"\x00\xFF\x2F\x00")
    return bytes(body)


def write_midi(path: Path, division: int, tracks: list[bytes]) -> None:
    data = bytearray()
    data.extend(b"MThd")
    data.extend(struct.pack(">IHHH", 6, 1, len(tracks), division))
    for track in tracks:
        data.extend(b"MTrk")
        data.extend(struct.pack(">I", len(track)))
        data.extend(track)
    path.write_bytes(bytes(data))


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge separate bass/guitar MIDI files into one type-1 MIDI.")
    parser.add_argument("directory", type=Path, help="Directory containing Electric Guitar.mid and Electric Bass.mid")
    parser.add_argument("--output", type=Path, help="Output MIDI path")
    args = parser.parse_args()

    directory = args.directory
    guitar_file = directory / "Electric Guitar.mid"
    bass_file = directory / "Electric Bass.mid"
    output = args.output or directory / f"{directory.name}.merged.mid"

    guitar = read_midi(guitar_file)
    bass = read_midi(bass_file)
    if guitar.division != bass.division:
        raise ValueError(f"Division mismatch: guitar {guitar.division}, bass {bass.division}")
    if len(guitar.tracks) < 2 or len(bass.tracks) < 2:
        raise ValueError("Expected each source MIDI to have a meta track and one note track")

    tracks = [
        make_meta_track(guitar.tracks[0], directory.name),
        make_part_track(guitar.tracks[1], "Electric Guitar", channel=0, program=29),
        make_part_track(bass.tracks[1], "Electric Bass", channel=1, program=33),
    ]
    write_midi(output, guitar.division, tracks)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
