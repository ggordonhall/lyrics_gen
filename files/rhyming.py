import re
import json

from pronouncing import rhymes


def build_dict(*files):
    """Read lyrics and construct rhyming dictionary"""
    rhyme_dict = {}
    dict_file = open("rhyme_dict.txt", 'w+')

    for file in files:
        with open(file, 'r+') as f:
            for line in f.readlines():
                words = line.strip().split(' ')
                if len(words) == 1 and words[0] == '':
                    continue
                stem = re.sub(r'[^\w\s]', '', words[-1]).lower()
                if stem not in dict.keys():
                    rhyme = rhymes(stem)
                    if rhyme:
                        rhyme_dict[stem] = rhyme

    dict_file.write(json.dumps(rhyme_dict))
    dict_file.close()


if __name__ == '__main__':
    VERSE = 'verse.txt'
    CHORUS = 'chorus.txt'
    build_dict(VERSE, CHORUS)
