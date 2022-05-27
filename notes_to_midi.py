import traceback
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from midiutil import MIDIFile
from note_utils import shifts, carnatic_keys
import re
import pygame
import argparse

key_map = {key: i for i, key in enumerate(carnatic_keys)}


def write_midi(notes, pitch='C', tempo=90, filename='example', instrument=104):
    track    = 0
    time     = 0    # In beats
    tempo    = tempo   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    shift = shifts[pitch]

    MyMIDI = MIDIFile(1, adjust_origin=False)
    MyMIDI.addTempo(track, time, tempo)
    MyMIDI.addProgramChange(0, 0, 0, instrument)

    t = 0
    for freq, duration in notes:
        MyMIDI.addNote(0, 0, 48 + freq + shift, t, duration / 4, volume)
        t += duration / 4

    if not os.path.exists('output'):
        os.mkdir('output')
    with open("output/{}.mid".format(filename), "wb") as output_file:
        MyMIDI.writeFile(output_file)


def get_notes_from_file(filename):
    notation = open(filename).read()
    notation = re.sub(r'[\s|]', '', notation)
    groups = re.split(r'([\<\(].*?[\)\>])', notation)
    all_notes = []
    for group in groups:
        if not group:
            continue
        multiplier = 3/2 if group[0] == '<' else (2 if group[0] == '(' else 1)
        note_strings = re.findall(r'([srgmpdnSRGMPDN][/*]*,*)', group)
        for n in note_strings:
            note, ups, downs, length = re.findall(r'([srgmpdnSRGMPDN])(\**)(/*)(,*)', n)[0]
            if note == 's' or note == 'p':
                note = note.upper()
            note_val = key_map[note]
            note_val += 12 * len(ups)
            note_val -= 12 * len(downs)
            duration = 1 + len(length)
            duration /= multiplier
            all_notes.append((note_val, duration))
    return all_notes


if __name__ == '__main__':
    options = [
        'piano',
        'sitar',
        'shanai',
        'overdriven_guitar',
        'accordion'
    ]
    midi_instruments = {
        'piano': 0,
        'sitar': 104,
        'shanai': 111,
        'overdriven_guitar': 29,
        'accordion': 21
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='file', nargs=1, help='Input notation file path')
    parser.add_argument('--pitch', '-p', type=str, choices=shifts.keys(),
                        default='C', dest='pitch', help='Pitch to generate sound in')
    parser.add_argument('--tempo', '-t', type=int, default=90, dest='tempo',
                        help='Tempo to generate sound at')
    parser.add_argument('--instrument', '-i', type=str, choices=options,
                        default='piano', dest='instrument', help='Instrument to generate sound in')
    args = parser.parse_args()

    try:
        notes = get_notes_from_file(args.file[0])
        name = '{}_{}_{}_{}'.format(args.file[0].split('.')[0].split('/')[-1], args.pitch, args.tempo, args.instrument)
        write_midi(notes, pitch=args.pitch, tempo=args.tempo, filename=name,
                   instrument=midi_instruments[args.instrument])
        print('Successfully outputted MIDI to {}.mid'.format(name))
        playback = input('Play back the song? (y/n) ')
        while playback == 'y':
            pygame.mixer.init()
            pygame.mixer.music.load(f'output/{name}.mid')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass
            playback = input('Play again? (y/n) ')

    except Exception as e:
        print('Error while outputting MIDI.')
        print(traceback.format_exc())
