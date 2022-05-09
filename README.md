# Innopolis-Music-Accompanement-Generation

This is the python script, used for generation of accompanement for the monophonic songs, written for Innopolis AI S22 course. It uses mainly the Circle of Fifth method for creating consonant chords, and then using them as a genetic function for genetic algorithm.

## Setup:
This program uses two libraries for its work: `music21` for simplifying detection of the song tonality and `mido` for parsing input, working with the midi format, and creating output song. The code was written on python, version: `Python 3.9.12.`

At the start of the program there are constraints  `INPUT_FILE_NAME='input1.mid'` and ` OUTPUT_FILE_NAME='output1.mid'`, that allow read/write MIDI files. 

In the pdf document there is the report, which analyzes and describes basical code's work principles.
