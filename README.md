# CarnaticMIDI

This project provides functionality to convert Carnatic notation into MIDI files. To install, begin by cloning this repository. Change to this repository's local directory and run:

`./install.sh`

This will install all the required packages and create a virtual environment called `carnatic`. Activate this virtual environment using:

`source carnatic/bin/activate`

Then execute:

`python midi_example.py`

# Creating notation files

The MIDI converter takes in any file which has notes according to the following structure. The 12 notes in the middle octave are represented as follows:

`S, r, R, g, G, m, M, P, d, D, n, N`

To make the note higher octave add a `*` after the note. To make the note lower octave, add a `/` after the note. The following is an example notation of the first line of the Bilahari swarajathi Rara Venu Gopabala:

`S,,RG,P,D,S*,N,D,P,DPmGRSRSN/D/S,,,`

The parser will ignore any character that is not one of the notes or `*` or `/`. This allows for spaces and newlines to format the notation to look nicer, such as the following:

`S,,R G,P, | D,S*, N,D, ||`

`P,DP mGRS | RSN/D/ S,,,`||`
