#!flask/bin/python
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

import random
import re
import ast
import markovify
from application.sylco import sylco
from string import capwords

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from application import application
from application.forms import UserName



# ELASTIC BEANSTALK INITIALISATION
# =====================================
application = Flask(__name__)
application.debug=True
application.secret_key = 'cC1YCIWOj9GgWspgNEo2'

# STRING FORMATTING
# =====================================

# Specify then remove punctuation
punc = set([',','.','"','?','!'])

def clean(str):
    if str[-1] in punc:
        return str[:-1].lower()
    return str.lower()

# Capitalise user-entered artist name
def cap_name(name):
    username = ''
    name_split = name.split(' ')
    for i in name_split:
        username += capwords(i) + ' '
    return username.strip()

# Insert username into the song where needed
def insert_username(song, username):
    song_edit = []
    for line in song:
        line = re.sub(r'XXXXX', username, line)
        song_edit.append(line)
    return song_edit

# Remove trailing commas from the end of verses
def clean_commas(song):
    res = []
    for idx,line in enumerate(song):
        try:
            if song[idx+1]=='' and line[-1]==',':
                res.append(line[:-1])
            else:
                res.append(line)
        except IndexError:
            return res

# MAIN FUNCTION LOGIC
# =====================================

# Fetch source text from files
chorus_text = str(open('files/lyrics_chorus.txt').read().strip())
verse_text = str(open('files/lyrics_verse.txt').read().strip())
chorus_rhymes = str(open('files/rhyme_dict_chorus.txt').read().strip())
verse_rhymes = str(open('files/rhyme_dict_verse.txt').read().strip())

# Model lyrics
chorus_model = markovify.NewlineText(chorus_text, state_size=2)
verse_model = markovify.NewlineText(verse_text, state_size=2)

# Evaluate tokenized text as sets
chorus_dict = ast.literal_eval(chorus_rhymes)
verse_dict = ast.literal_eval(verse_rhymes)

# Set guide number of syllables per line
VERSE_BENCH = random.randint(6,10)
CHORUS_BENCH = random.randint(3,8)
BRIDGE_BENCH = random.randint(3,6)

# Define then set rhyming patterns for verse and chorus
verse_patterns = ['AABBCC', 'ABABCC', 'AABBC', 'ABABCDCD', 'AAAA']
chorus_patterns = ['AA', 'ABAB', 'AABB', 'AAAA']
VERSE_PATTERN = random.choice(verse_patterns)
CHORUS_PATTERN = random.choice(chorus_patterns)

# Generate line that rhymes with line stem
def match_rhyme(stem, model, bench, d):

    # Check if rhymes exist
    try:
        ls = d[stem]
        if ls == []:
            return None
    except KeyError:
        return None


    # If rhymes exist, test for rhymes by generating lines
    for n in range(100):
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
                if rhyme_stem in ls:
                    return rhyme_line

                # After a point, accept if rhyme_stem == stem
                if n > 50:
                    if rhyme_stem == stem:
                        return rhyme_line

                break
    return None

# Construct verse for given rhyming pattern
def make_verse():
    verse = []
    pattern = VERSE_PATTERN
    stems = {}

    for idx, i in enumerate(pattern):
        while True:
            a = idx - 1
            b = idx - 2

            # Try to find rhyming match based on the rhyming pattern
            try:
                if a >= 0 and i == pattern[a]:
                    match = match_rhyme(stems[a], verse_model, VERSE_BENCH, verse_dict)

                    if match:

                        # Cache line stem and add matching line to verse
                        stems[idx] = clean(match.rsplit(None, 1)[-1])
                        verse.append(match)
                        break

                elif b >= 0 and i == pattern[b]:
                    match = match_rhyme(stems[b], verse_model, VERSE_BENCH, verse_dict)

                    if match:

                        # Cache line stem and add matching line to verse
                        stems[idx] = clean(match.rsplit(None, 1)[-1])
                        verse.append(match)
                        break

            except IndexError:
                pass

            # Otherwise add non-rhyming markovify line
            line = verse_model.make_sentence()
            if line:

                # Keep syllables within verse range
                syl_count = sylco(line)
                if syl_count > (VERSE_BENCH + 2) or syl_count < (VERSE_BENCH - 2):
                    continue

                # Cache line stem for future rhymes and add to verse
                stems[idx] = clean(line.rsplit(None, 1)[-1])
                verse.append(line)
                break

    verse.append('')
    return verse

# Construct chorus for given rhyming pattern
def make_chorus():
    chorus = ['[Chorus]']
    pattern = CHORUS_PATTERN
    stems = {}

    for idx, i in enumerate(pattern):
        while True:
            a = idx - 1
            b = idx - 2

            # Try to find rhyming match based on the rhyming pattern
            try:
                if a >= 0 and i == pattern[a]:
                    match = match_rhyme(stems[a], chorus_model, CHORUS_BENCH, chorus_dict)

                    if match:

                        # Cache line stem and add matching line to chorus
                        stems[idx] = clean(match.rsplit(None, 1)[-1])
                        chorus.append(match)
                        break

                elif b >= 0 and i == pattern[b]:
                    match = match_rhyme(stems[b], chorus_model, CHORUS_BENCH, chorus_dict)

                    if match:

                        # Cache line stem and add matching line to chorus
                        stems[idx] = clean(match.rsplit(None, 1)[-1])
                        chorus.append(match)
                        break

            except IndexError:
                pass

            # Otherwise add non-rhyming markovify line
            line = chorus_model.make_sentence()
            if line:

                # Keep syllables within chorus range
                syl_count = sylco(line)
                if syl_count > (CHORUS_BENCH + 2) or syl_count < (CHORUS_BENCH - 2):
                    continue

                # Cache line stem for future rhymes and add to chorus
                stems[idx] = clean(line.rsplit(None, 1)[-1])
                chorus.append(line)
                break

    chorus.append('')
    return chorus

# Construct pre-chorus
def make_prechorus():
    prechorus = []
    stem = 0

    # Two rhyming lines
    for _ in range(2):
        while True:

            # Try to match line
            if _ == 1:
                match = match_rhyme(stem, verse_model, VERSE_BENCH, verse_dict)

                # If match, add to bridge
                if match:
                    prechorus.append(match)
                    break

            line = verse_model.make_sentence()
            if line:

                # Keep syllables within bridge range
                syl_count = sylco(line)
                if syl_count > (VERSE_BENCH + 1) or syl_count < (VERSE_BENCH - 1):
                    continue

                # Cache line for rhyming
                if _ == 0:
                    stem = clean(line.rsplit(None, 1)[-1])

                prechorus.append(line)
                break

    prechorus.append('')
    return prechorus

# Construct bridge
def make_bridge():
    bridge = ['[Bridge]']
    stem = 0

    # Two rhyming lines
    for _ in range(2):
        while True:

            # Try to match line
            if _ == 1:
                match = match_rhyme(stem, chorus_model, BRIDGE_BENCH, chorus_dict)

                # If match, add to bridge
                if match:
                    bridge.append(match)
                    break

            line = chorus_model.make_sentence()
            if line:

                # Keep syllables within bridge range
                syl_count = sylco(line)
                if syl_count > (BRIDGE_BENCH + 1) or syl_count < (BRIDGE_BENCH - 1):
                    continue

                # Cache line for rhyming
                if _ == 0:
                    stem = clean(line.rsplit(None, 1)[-1])

                bridge.append(line)
                break

    # One short line
    while True:
        line = chorus_model.make_short_sentence(40)

        if line:
            bridge.append(line + '...')
            break

    bridge.append('')
    return bridge

# Construct fadeout
def fadeout(chorus):
    fadeout = ['[Fade]', chorus[-2]]
    for i in range(2):
        fadeout.append(chorus[-2].rsplit(None, (i+1))[0])
    fadeout.append('')
    return fadeout

# Construct song
def make_song():
    song = []

    # Set chorus
    song_chorus = make_chorus()

    # Set variables
    my_funcs = {
    'V' : make_verse,
    'B' : make_bridge,
    'P' : make_prechorus,
    'E' : make_chorus, # Alternate chorus
    }

    # Define song structures
    structs = ['VPCVBCC', 'VCVVCF', 'VVPCCF', 'VCVBCCF', 'VPCCVBCF', 'VCVCCF', 'VPCBCF', \
            'VVPCVBCC', 'VCVCF', 'VPCVVBCF', 'VVVCBCEC', 'VCVCEC', 'EVVCBC', 'PCVECCF']

    # Randomly choose structure
    struct = random.choice(structs)

    # Iterate over structure and add results to song string
    for elem in struct:
        if elem == 'C':
            song.extend(song_chorus)
        elif elem == 'F':
            song.extend(fadeout(song_chorus))
        else:
            func_call = my_funcs[elem]
            song.extend(func_call())

    return song

# Set the song name using lyrics
def set_name(song):
    song_name = ''
    punc = set([',','.','"'])

    # Discard unwanted lines
    junk = ['', '[Chorus]', '[Bridge]']
    lines = [line for line in song if line not in junk and len(line.split(' '))!=1]

    # Choose random line, start and stop indicies
    line = random.choice(lines).split(' ')
    start = random.randint(0,len(line)-2)
    stop = random.randint(start+1,len(line)-1)
    l = line[start:stop+1]

    # Add words within range to string and capitalise the first word
    for idx,word in enumerate(l):

        # Check for trailing punctuation and remove unless ellipsis
        if idx == len(l)-1 and word[-1] in punc and word[-3:] != "...":
            song_name += (capwords(word[:-1]) + ' ')
        else:
            song_name += (capwords(word) + ' ')

    song_name.strip()

    return song_name

# ROUTES
# =====================================

@application.route('/', methods=['POST', 'GET'])
def login():
    form = UserName()
    if form.validate_on_submit():
        name = request.form['artistName']
        return redirect(url_for('result', name=name))
    return render_template('homepage.html', form=form)

@application.route('/result')
def result():
    username = cap_name(request.args['name'])
    lyrics = make_song()
    lyrics = clean_commas(lyrics)
    lyrics = insert_username(lyrics,username)
    song_name = set_name(lyrics)
    return render_template('resultpage.html', username=username, lyrics=lyrics, song_name=song_name)

if __name__ == '__main__':
    application.run()
