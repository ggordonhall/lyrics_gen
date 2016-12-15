#!/usr/bin/env python
import random
import markovify
import ast
from rhyme import rhyme_finder
from sylco import sylco

# Open and model lyrics
with open('lyrics_verse.txt') as f:
    verse_text = f.read()
with open('lyrics_chorus.txt') as f:
    chorus_text = f.read()
with open('tokenized_verse.txt') as f:
    tokenized_verse = f.read()
with open('tokenized_chorus.txt') as f:
    tokenized_chorus = f.read()

verse_model = markovify.NewlineText(verse_text, state_size=2)
chorus_model = markovify.NewlineText(chorus_text, state_size=2)

# Evaluate tokenized text as sets
tokenized_verse = set(ast.literal_eval(tokenized_verse))
tokenized_chorus = set(ast.literal_eval(tokenized_chorus))

# Specify then remove punctuation
punc = set([',','.','"','?','!'])

def clean(str):
    if str[-1] in punc:
        return str[:-1].lower()
    return str.lower()

# Set guide number of syllables per line
VERSE_BENCH = random.randint(6,12)
CHORUS_BENCH = random.randint(3,8)
BRIDGE_BENCH = random.randint(3,6)

# Generate line that rhymes with line stem
def match_rhyme(stem, model, bench, text):

    # Check if rhymes exist
    try:
        ls = rhyme_finder(stem, text)
    except KeyError:
        return None
    if not ls:
        return None

    # If rhymes exist, test for rhymes by generating lines
    for n in range(50):
        while True:
            rhyme_line = model.make_sentence()

            if rhyme_line:

                # Keep syllables within range
                syl_count = sylco(rhyme_line)
                if syl_count > (bench + 2) or syl_count < (bench - 2):
                    continue

                # Get stem of rhyme_line
                rhyme_stem = clean(rhyme_line.rsplit(None, 1)[-1])

                # Check for rhyme
                if rhyme_stem == stem or rhyme_stem in ls:
                    return rhyme_line

                break
    return None

# Construct 6-line verse
def make_verse():
    verse = ''
    stem1 = None
    stem2 = None
    stem3 = None

    # Markovify for each line
    for _ in range(6):
        while True:

            # Try to find rhyming match between lines 1 and 3
            if _ == 2:
                match = match_rhyme(stem1, verse_model, VERSE_BENCH, tokenized_verse)

                # If match, add to verse
                if match:
                    verse += (match + '\n')
                    break

            # Try to find rhyming match between lines 2 and 4
            elif _ == 3:
                match = match_rhyme(stem2, verse_model, VERSE_BENCH, tokenized_verse)

                # If match, add to verse.
                if match:
                    verse += (match + '\n')
                    break

            # Try to find rhyming match between lines 5 and 6
            elif _ == 5:
                match = match_rhyme(stem3, verse_model, VERSE_BENCH, tokenized_verse)

                # If match, add to verse
                if match:
                    verse += (match + '\n')
                    break

            # Otherwise add non-rhyming markovify line
            line = verse_model.make_sentence()

            if line:

                # Keep syllables within verse range
                syl_count = sylco(line)
                if syl_count > (VERSE_BENCH + 2) or syl_count < (VERSE_BENCH - 2):
                    continue

                # Cache line for rhyming
                if _ == 0:
                    stem1 = clean(line.rsplit(None, 1)[-1])
                elif _ == 1:
                    stem2 = clean(line.rsplit(None, 1)[-1])
                elif _ == 4:
                    stem3 = clean(line.rsplit(None, 1)[-1])

                verse += (line + '\n')
                break

    return verse

# Construct chorus
def make_chorus():
    chorus = '[Chorus]' + '\n'
    stem1 = 0
    stem2 = 0

    # Four rhyming lines
    for _ in range(4):
        while True:

            # Try to find rhyming match between lines 1 and 2
            if _ == 1:
                match = match_rhyme(stem1, chorus_model, CHORUS_BENCH, tokenized_chorus)

                # If match, add to chorus
                if match:
                    chorus += (match + '\n')
                    break

            # Try to find rhyming match between lines 3 and 4
            elif _ == 3:
                match = match_rhyme(stem2, chorus_model, CHORUS_BENCH, tokenized_chorus)

                # If match, add to chorus
                if match:
                    chorus += (match + '\n')
                    break

            line = chorus_model.make_sentence()
            if line:

                # Keep syllables within chorus range
                syl_count = sylco(line)
                if syl_count > (CHORUS_BENCH + 2) or syl_count < (CHORUS_BENCH - 2):
                    continue

                # Cache line for rhyming
                if _ == 0:
                    stem1 = clean(line.rsplit(None, 1)[-1])
                elif _ == 2:
                    stem2 = clean(line.rsplit(None, 1)[-1])

                chorus += (line + '\n')
                break

    return chorus

# Construct pre-chorus
def make_prechorus():
    prechorus = ''
    stem = 0

    # Two rhyming lines
    for _ in range(2):
        while True:

            # Try to match line
            if _ == 1:
                match = match_rhyme(stem, verse_model, VERSE_BENCH, tokenized_verse)

                # If match, add to bridge
                if match:
                    prechorus += (match + '\n')
                    break

            line = verse_model.make_sentence()
            if line:

                # Keep syllables within bridge range
                syl_count = sylco(line)
                if syl_count > (VERSE_BENCH + 2) or syl_count < (VERSE_BENCH - 2):
                    continue

                # Cache line for rhyming
                if _ == 0:
                    stem = clean(line.rsplit(None, 1)[-1])

                prechorus += (line + '\n')
                break

    return prechorus

# Construct bridge
def make_bridge():
    bridge = '[Bridge]' + '\n'
    stem = 0

    # Two rhyming lines
    for _ in range(2):
        while True:

            # Try to match line
            if _ == 1:
                match = match_rhyme(stem, chorus_model, BRIDGE_BENCH, tokenized_chorus)

                # If match, add to bridge
                if match:
                    bridge += (match + '\n')
                    break

            line = chorus_model.make_sentence()
            if line:

                # Keep syllables within bridge range
                syl_count = sylco(line)
                if syl_count > (BRIDGE_BENCH + 2) or syl_count < (BRIDGE_BENCH - 2):
                    continue

                # Cache line for rhyming
                if _ == 0:
                    stem = clean(line.rsplit(None, 1)[-1])

                bridge += (line + '\n')
                break

    # One short line
    while True:
        line = chorus_model.make_short_sentence(40)

        if line:
            bridge += (line + '...' + '\n')
            break

    return bridge

# Construct song
def make_song():
    song = ''

    song_chorus = make_chorus()

    # Set variables and generate chorus
    my_funcs = {
    'V' : make_verse,
    'B' : make_bridge,
    'P' : make_prechorus}

    # Define song structures
    structs = ['VPCVBCC', 'VCVVC', 'VVPCC', 'VCVBCC', 'VPCCVBC', 'VCVCC', 'VPCBC', \
            'VVPCVBCC', 'VCVC', 'VPCVVBC']

    # Randomly choose structure
    struct = random.choice(structs)

    # Iterate over structure and add results to song string
    for elem in struct:
        if elem == 'C':
            song += song_chorus + '\n'
        else:
            func_call = my_funcs[elem]
            song += func_call() + '\n'
    return song

print (make_song())
