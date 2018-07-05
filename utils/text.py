from random import randint, choice
from string import capwords


def clean(string):
    """
    Remove punctuation from string, unless
    last character is punctuation.
    """
    punctuation = {',', '.', '"', '?', '!'}
    if string[-1] in punctuation:
        return string[:-1].lower()
    return string.lower()


def cap_name(name):
    """
    Capitalise user-entered artist name.
    """
    username = ''
    for i in name.split(' '):
        username += capwords(i) + ' '
    return username.strip()


def clean_commas(song):
    """
    Remove trailing commas from the end of a
    verse.
    """
    res = []
    for idx in range(len(song)):
        if song[idx][-1] == ',':
            if idx + 1 >= len(song) or song[idx + 1] == '':
                res.append(song[idx][:-1])
        else:
            res.append(song[idx])
    return res


def insert_username(song, username):
    """
    Insert username into the song where specified
    """
    return song.replace('XXXXX', username)


def set_name(song):
    """Choose random section of lyrics for title"""
    # Discard unwanted lines
    junk = ['', '[Chorus]', '[Bridge]']
    lines = [line for line in song.split('\n') if line not in junk and len(
        line.split(' ')) != 1]

    # Choose random line, start and stop indicies
    line = choice(lines).split(' ')
    start = randint(0, len(line)-2)
    stop = randint(start+1, len(line)-1)
    l = line[start:stop+1]

    # Add words within range to string and capitalise the first word
    song_name = ''
    punc = set([',', '.', '"'])
    for idx, word in enumerate(l):
        # Check for trailing punctuation and remove unless ellipsis
        if idx == len(l)-1 and word[-1] in punc and word[-3:] != "...":
            song_name += (capwords(word[:-1]) + ' ')
        else:
            song_name += (capwords(word) + ' ')
    song_name.strip()
    return song_name
