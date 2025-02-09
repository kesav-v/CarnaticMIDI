from typing import List, Dict
from dataclasses import dataclass
from midiutil import MIDIFile
from note_utils import shifts, MIDDLE_C

MIDI_INSTRUMENTS = {
    "piano": 0,
    "sitar": 104,
    "shanai": 111,
    "overdriven_guitar": 29,
    "accordion": 21,
}
MUSIC_CHANNEL = 0
BEATS_TRACK = 1
BEATS_CHANNEL = 9
BASS_NOTE = 35


@dataclass
class Note:
    shift: int
    duration: float
    octave_shift: int


class Chord:
    def __init__(self):
        self._notes: List[Note] = []
        self._current_duration = 0

    def add_note(self, note: Note) -> None:
        self._notes.append(note)

    def increment_duration(self, amount: float) -> None:
        self._current_duration += amount

    def current_note(self) -> Note:
        return self._notes[self._current_duration % len(self._notes)]


class Beat:
    def __init__(
        self,
        length: int,
        beat_positions: List[int],
        note: int = BASS_NOTE,
    ) -> None:
        self._length = length
        self._beat_positions = set(beat_positions)
        self.note = note
        self._current_duration = 0

    def increment_duration(self) -> None:
        self._current_duration += 1

    def should_play(self) -> bool:
        return self._current_duration % self._length in self._beat_positions


class MIDIFileBuilder:
    def __init__(self, pitch: str, tempo: int, instrument: str) -> None:
        self._pitch = pitch
        self._tempo = tempo
        self._instrument = MIDI_INSTRUMENTS[instrument]
        self._base_shift = shifts[pitch]
        self._notes: List[Note] = []
        self._midi = self._set_up_midi_object()
        self._volume = 100
        self._current_time = 0.0
        self._beats: Dict[str, Beat] = {}
        self._chords: Dict[str, Chord] = {}

    def _set_up_midi_object(self) -> MIDIFile:
        # Music channel.
        MyMIDI = MIDIFile(2, adjust_origin=False)
        MyMIDI.addTempo(0, MUSIC_CHANNEL, self._tempo)  # type: ignore
        MyMIDI.addProgramChange(0, MUSIC_CHANNEL, 0, self._instrument)  # type: ignore
        # Beats channel.
        MyMIDI.addTempo(BEATS_TRACK, MUSIC_CHANNEL, self._tempo)  # type: ignore
        MyMIDI.addProgramChange(BEATS_TRACK, BEATS_CHANNEL, 0, 96)  # type: ignore
        return MyMIDI

    def add_chord(self, name: str, chord: Chord) -> None:
        if name in self._chords:
            raise ValueError(f"Duplicate chord with name {name}")
        self._chords[name] = chord

    def add_note(self, note: Note) -> None:
        self._midi.addNote(  # type: ignore
            0,
            MUSIC_CHANNEL,
            MIDDLE_C + note.shift + self._base_shift + 12 * note.octave_shift,
            self._current_time,
            note.duration / 4,
            self._volume,
        )
        self._add_all_active_beats(note.duration)
        self._add_all_active_chords(note.duration)
        self._current_time += note.duration / 4

    def _add_all_active_chords(self, note_duration: float) -> None:
        for chord in self._chords.values():
            current_time = self._current_time
            while current_time < self._current_time + note_duration / 4:
                note = chord.current_note()
                self._midi.addNote(
                    0,
                    MUSIC_CHANNEL,
                    MIDDLE_C + note.shift + self._base_shift + 12 * note.octave_shift,
                    current_time,
                    note.duration / 4,
                    self._volume,
                )
                chord.increment_duration(note.duration)

    def add_beat(self, name: str, beat: Beat) -> None:
        if name in self._beats:
            raise ValueError(f"Duplicate beat with name {name}")
        self._beats[name] = beat

    def remove_beat(self, name: str) -> None:
        if name not in self._beats:
            raise ValueError(f"Beat with name {name} not found")
        del self._beats[name]

    def _add_all_active_beats(self, note_duration: float) -> None:
        for beat in self._beats.values():
            current_time = self._current_time
            while current_time < self._current_time + note_duration / 4:
                if beat.should_play():
                    self._midi.addNote(  # type: ignore
                        BEATS_TRACK,
                        BEATS_CHANNEL,
                        beat.note,
                        current_time,
                        1 / 4,
                        self._volume,
                    )
                beat.increment_duration()
                current_time += 1 / 4

    def dump(self, file_name: str) -> None:
        with open(file_name, "wb") as f:
            self._midi.writeFile(f)  # type: ignore
