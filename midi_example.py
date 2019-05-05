import traceback

from midiutil import MIDIFile
from note_utils import shifts, carnatic_keys
import re

key_map = {key: i for i, key in enumerate(carnatic_keys)}

def write_midi(notes, pitch='C', tempo=90, filename='example'):
    track    = 0
    time     = 0    # In beats
    tempo    = tempo * 4   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    shift = shifts[pitch]

    MyMIDI = MIDIFile(1, adjust_origin=False)
    MyMIDI.addTempo(track, time, tempo)
    MyMIDI.addProgramChange(0, 0, 0, 104)

    t = 0
    for freq, duration in notes:
        MyMIDI.addNote(0, 0, 48 + freq + shift, t, duration, volume)
        t += duration

    with open("{}.mid".format(filename), "wb") as output_file:
        MyMIDI.writeFile(output_file)

def get_notes_from_file(filename):
    notation = open(filename).read()
    notation = re.sub(r'[\s|]', '', notation)
    groups = re.split(r'(\(.*?\))', notation)
    all_notes = []
    for group in groups:
        if not group:
            continue
        half_dur = group[0] == '('
        note_strings = re.findall(r'([srgmpdnSRGMPDN][/*]*,*)', group)
        for n in note_strings:
            note, ups, downs, length = re.findall(r'([srgmpdnSRGMPDN])(\**)(/*)(,*)', n)[0]
            note_val = key_map[note]
            note_val += 12 * len(ups)
            note_val -= 12 * len(downs)
            duration = 1 + len(length)
            if half_dur:
                duration /= 2
            all_notes.append((note_val, duration))
    return all_notes

if __name__ == '__main__':
    while True:
        try:
            filename = input('Enter notation file name -> ')
            notes = get_notes_from_file(filename)
            break
        except:
            print('Error processing notation file, please try again.')
            continue
    pitch = input('Enter pitch -> ')
    tempo = int(input('Enter tempo -> '))
    try:
        name = '{}_{}_{}'.format(filename.split('.')[0], pitch, tempo)
        write_midi(notes, pitch=pitch, tempo=tempo, filename=name)
        print('Successfully outputted MIDI to {}.mid'.format(name))
    except:
        print('Error while outputting MIDI.')
        print(traceback.format_exc())