from random import randint, choice
from string import capwords

from typing import List


def data_window(path: str, window: int) -> str:
    """
    Open lyrics file and select a random
    window of consecutive lines.
    """
    with open(path, "r") as f:
        lines = f.readlines()
        line_count = len(lines)
        base = randint(0, line_count - (window + 1))
        data_slice = lines[base: base + window]
        return '\n'.join(data_slice)


def clean(string: str) -> str:
    """
    Remove punctuation from string, unless
    last character is punctuation.
    """
    punctuation = {',', '.', '"', '?', '!'}
    if string[-1] in punctuation:
        string = string[:-1]
    return string.lower()


def cap_name(name: str) -> str:
    """
    Capitalise user-entered artist name.
    """
    username = [capwords(i) for i in name.split()]
    return ' '.join(username)


def clean_commas(song_list: List[str]) -> List[str]:
    """
    Remove trailing commas from the end of a
    verse.
    """
    res = []
    for idx, line in enumerate(song_list):
        if line[-1] == ',':
            if idx + 1 >= len(song_list) or song_list[idx + 1] == '':
                line = line[:-1]
        res.append(line)
    return res


def insert_username(song: str, username: str) -> str:
    """
    Insert username into the song where specified
    """
    return song.replace('XXXXX', username)


def set_name(song: str) -> str:
    """Choose random section of lyrics for title"""
    # Discard unwanted lines
    junk = ['', '[Chorus]', '[Bridge]']
    lines = [line for line in song.split('\n') if line not in junk and len(
        line.split(' ')) != 1]

    # Choose random line, start and stop indicies
    line = choice(lines).split(' ')
    start = randint(0, len(line)-2)
    stop = randint(start+1, len(line)-1)
    line = line[start:stop+1]

    # Add words within range to string and capitalise the first word
    song_name = []
    punc = set([',', '.', '"'])
    for idx, word in enumerate(line):
        # Check for trailing punctuation and remove unless ellipsis
        if idx == len(line)-1 and word[-1] in punc and word[-3:] != "...":
            word = word[:-1]
        song_name.append(capwords(word))
    return ' '.join(song_name)
