import random
import ast
import markovify
from .sylco import sylco
from string import capwords

from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from app import app
from .forms import UserName
from .models import SourceText, SourceRhymes

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

# Fetch source text from the database
chorus_text = str(SourceText.query.get(1))
verse_text = str(SourceText.query.get(2))
chorus_rhymes = str(SourceRhymes.query.get(1))
verse_rhymes = str(SourceRhymes.query.get(2))

# Model lyrics
chorus_model = markovify.NewlineText(chorus_text, state_size=2)
verse_model = markovify.NewlineText(verse_text, state_size=2)

# Evaluate tokenized text as sets
chorus_dict = ast.literal_eval(chorus_rhymes)
verse_dict = ast.literal_eval(verse_rhymes)

# Set guide number of syllables per line
VERSE_BENCH = random.randint(6,12)
CHORUS_BENCH = random.randint(3,8)
BRIDGE_BENCH = random.randint(3,6)

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
    verse = []
    stem1 = None
    stem2 = None
    stem3 = None

    # Markovify for each line
    for _ in range(6):
        while True:

            # Try to find rhyming match between lines 1 and 3
            if _ == 2:
                match = match_rhyme(stem1, verse_model, VERSE_BENCH, verse_dict)

                # If match, add to verse
                if match:
                    verse.append(match)
                    break

            # Try to find rhyming match between lines 2 and 4
            elif _ == 3:
                match = match_rhyme(stem2, verse_model, VERSE_BENCH, verse_dict)

                # If match, add to verse.
                if match:
                    verse.append(match)
                    break

            # Try to find rhyming match between lines 5 and 6
            elif _ == 5:
                match = match_rhyme(stem3, verse_model, VERSE_BENCH, verse_dict)

                # If match, add to verse
                if match:
                    verse.append(match)
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

                verse.append(line)
                break

    verse.append('')
    return verse

# Construct chorus
def make_chorus():
    chorus = ['[Chorus]']
    stem1 = 0
    stem2 = 0

    # Four rhyming lines
    for _ in range(4):
        while True:

            # Try to find rhyming match between lines 1 and 2
            if _ == 1:
                match = match_rhyme(stem1, chorus_model, CHORUS_BENCH, chorus_dict)

                # If match, add to chorus
                if match:
                    chorus.append(match)
                    break

            # Try to find rhyming match between lines 3 and 4
            elif _ == 3:
                match = match_rhyme(stem2, chorus_model, CHORUS_BENCH, chorus_dict)

                # If match, add to chorus
                if match:
                    chorus.append(match)
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
                if syl_count > (VERSE_BENCH + 2) or syl_count < (VERSE_BENCH - 2):
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
                if syl_count > (BRIDGE_BENCH + 2) or syl_count < (BRIDGE_BENCH - 2):
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

# Construct song
def make_song():
    song = []

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
            song.extend(song_chorus)
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
    lines = [line for line in song if line not in junk]

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

    return song_name.strip()

# ROUTES
# =====================================

@app.route('/', methods=['POST', 'GET'])
def login():
    form = UserName()
    if form.validate_on_submit():
        name = request.form['artistName']
        return redirect(url_for('result', name=name))
    return render_template('home.html', form=form)

@app.route('/result')
def result():
    song = make_song()
    song = clean_commas(song)
    song_name = set_name(song)
    username = cap_name(request.args['name'])
    return render_template('result.html', username=username, song=song, song_name=song_name)
