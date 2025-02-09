import lark
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
import midi_file_builder
import lark.visitors
import argparse
from typing import Any, List
from note_utils import shifts, carnatic_keys_to_shifts


CARNATIC_GRAMMAR_PATH = "carnatic_notation_grammar.lark"
UPPER_OCTAVE = "UPPER_OCTAVE"
LOWER_OCTAVE = "LOWER_OCTAVE"
KARVE = "KARVE"
BEAT = "BEAT"


def _get_output_file_base_name(
    file_name: str, pitch: str, tempo: int, instrument: str
) -> str:
    base_name = os.path.basename(file_name).split(".")[0]
    return "output/{}_{}_{}_{}.mid".format(base_name, pitch, tempo, instrument)


class NotesParser:
    _grammar: str | None = None

    def __init__(self) -> None:
        self._lark = lark.Lark(self.grammar, start="start", parser="lalr")

    @property
    def grammar(self) -> str:
        if self._grammar is None:
            with open(CARNATIC_GRAMMAR_PATH) as f:
                self._grammar = f.read()
        return self._grammar

    def parse(self, text: str) -> lark.ParseTree:
        return self._lark.parse(text)


class NotesVisitor(lark.visitors.Visitor):  # type: ignore

    def __init__(self, pitch: str, tempo: int, instrument: str) -> None:
        super().__init__()
        self._midi_file_builder = midi_file_builder.MIDIFileBuilder(
            pitch, tempo, instrument
        )
        self._speedup: int = 0
        self._current_chord: midi_file_builder.Chord | None = None

    def speedup(self, _speedup_tree: Any) -> None:
        self._speedup += 1

    def slowdown(self, _slowdown_tree: Any) -> None:
        self._speedup -= 1

    def beat(self, beat_tree: Any) -> None:
        name = beat_tree.children[0].children[0].value
        beat_positions: List[int] = []
        beat_signals = beat_tree.children[1:-1]
        note_token = beat_tree.children[-1]
        note = midi_file_builder.BASS_NOTE
        if note_token is not None:
            note = int(note_token)
        length = len(beat_signals)
        for i, token in enumerate(beat_signals):
            if token.type == BEAT:
                beat_positions.append(i)
        self._midi_file_builder.add_beat(
            name, midi_file_builder.Beat(length, beat_positions, note=note)
        )

    def chord(self, chord_tree: Any) -> None:
        name = chord_tree.children[0].children[0].value
        self._current_chord = midi_file_builder.Chord()
        self._midi_file_builder.add_chord(name, self._current_chord)

    def stop_expression(self, stop_tree: Any) -> None:
        name = stop_tree.children[0].children[0].value
        self._midi_file_builder.remove_beat(name)

    def note(self, note_tree: Any) -> None:
        base_note = note_tree.children[0].value
        shift = carnatic_keys_to_shifts[base_note]
        octave_shift = 0
        duration = 1
        for token in note_tree.children[1:]:
            assert isinstance(token, lark.Token)
            if token.type == UPPER_OCTAVE:
                octave_shift += 1
            elif token.type == LOWER_OCTAVE:
                octave_shift -= 1
            elif token.type == KARVE:
                duration += 1
        duration /= 2**self._speedup
        current_note = midi_file_builder.Note(shift, duration, octave_shift)
        if self._current_chord:
            self._current_chord.add_note(current_note)
        else:
            self._midi_file_builder.add_note(current_note)

    def dump_to_midi_file(self, file_name: str) -> None:
        self._midi_file_builder.dump(file_name)


def output_midi_file(file_name: str, pitch: str, tempo: int, instrument: str) -> str:
    with open(file_name) as f:
        content = f.read()
    notes_parser = NotesParser()
    parse_tree = notes_parser.parse(content)
    visitor = NotesVisitor(pitch, tempo, instrument)
    visitor.visit_topdown(parse_tree)  # type: ignore
    file_path = _get_output_file_base_name(file_name, pitch, tempo, instrument)
    visitor.dump_to_midi_file(
        _get_output_file_base_name(file_name, pitch, tempo, instrument)
    )
    return file_path


def _maybe_play_midi_file(file_path: str) -> None:
    print("Successfully outputted MIDI to {}".format(file_path))
    playback = input("Play back the song? (y/n) ")
    while playback == "y":
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass
        playback = input("Play again? (y/n) ")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file", metavar="file", nargs=1, help="Input notation file path"
    )
    parser.add_argument(
        "--pitch",
        "-p",
        type=str,
        choices=shifts.keys(),
        default="C",
        dest="pitch",
        help="Pitch to generate sound in",
    )
    parser.add_argument(
        "--tempo",
        "-t",
        type=int,
        default=90,
        dest="tempo",
        help="Tempo to generate sound at",
    )
    parser.add_argument(
        "--instrument",
        "-i",
        type=str,
        choices=midi_file_builder.MIDI_INSTRUMENTS.keys(),
        default="piano",
        dest="instrument",
        help="Instrument to generate sound in",
    )
    args = parser.parse_args()
    file_path = output_midi_file(args.file[0], args.pitch, args.tempo, args.instrument)
    _maybe_play_midi_file(file_path)


if __name__ == "__main__":
    main()
