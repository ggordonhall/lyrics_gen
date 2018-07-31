import re
import operator
import functools

import time


def make_word_list(tokenized_text, d):
    word_list = []
    for i in tokenized_text:
        try:
            d[i.lower()]
        except KeyError:
            pass
        else:
            if i.lower() == "'s":
                pass
            elif i[-1] == ".":
                pass
            else:
                word_list.append((i.lower(), d[i.lower()][0]))
    return word_list


def meter(word, d):
    pron = d[word]
    m1, m2, mx = [], [], []
    # Find the order of numbers in pronunciation, where numbers
    # signify vowels.
    if len(pron) == 1:
        for i in pron[0]:
            if '0' in i:
                m1.append(0)
            elif '1' in i:
                m1.append(1)
            elif '2' in i:
                m1.append(2)
            else:
                pass
        mx = [m1]
    # If there are two or more possible pronunciations, find the
    # number order for the first two. Then set to the variable mx.
    elif len(pron) >= 2:
        for i in pron[0]:
            if '0' in i:
                m1.append(0)
            elif '1' in i:
                m1.append(1)
            elif '2' in i:
                m1.append(2)
            else:
                pass
        for i in pron[1]:
            if '0' in i:
                m2.append(0)
            elif '1' in i:
                m2.append(1)
            elif '2' in i:
                m2.append(2)
            else:
                pass
        mx = [m1, m2]
    m = []
    # If there is only one possible pronunciation
    if len(mx) == 1:
        # Multiply list of breakpoints together
        w0 = functools.reduce(operator.mul, mx[0], 1)
        if w0 >= 2:
            # If multiple >= 2 assign breakpoint 1 unstressed
            # vowel and breakpoint 2 stressed vowel
            for i in mx[0]:
                if i == 1:
                    m.append('u')
                elif i == 2:
                    m.append('s')
        elif w0 == 1:
            # If multiple == 1 then every vowel is stressed
            for i in mx[0]:
                m.append('s')
        elif w0 == 0:
            # If multiple == 0 then every 0 vowel is unstressed
            # whereas the others are stressed
            for i in mx[0]:
                if i == 0:
                    m.append('u')
                elif i == 1 or i == 2:
                    m.append('s')
    # Variable m is a list of the order of stressed/unstressed vowels

    # If there are two possible pronunciation then return a hybrid
    # vowel stress list
    elif len(mx) == 2:
        w0 = functools.reduce(operator.mul, mx[0], 1)
        w1 = functools.reduce(operator.mul, mx[1], 1)
        if w0 >= 2 and w1 >= 2:
            for (i, j) in zip(mx[0], mx[1]):
                if i * j == 1:
                    m.append('u')
                elif i * j == 4:
                    m.append('s')
                elif i * j == 2:
                    m.append('x')
        elif w0 == 1 and w1 == 1:
            for (i, j) in zip(mx[0], mx[1]):
                m.append('s')
        elif w0 == 0 and w1 == 0:
            for (i, j) in zip(mx[0], mx[1]):
                if i == j and i * j >= 1:
                    m.append('s')
                elif i != j and i * j == 0:
                    m.append('x')
                elif i == j and i * j == 0:
                    m.append('u')
        elif w0 >= 2 and w1 == 0:
            for (i, j) in zip(mx[0], mx[1]):
                if i == 1 and j == 0:
                    m.append('u')
                elif i == 2 and j == 0:
                    m.append('x')
                elif i == 1 and j == 1:
                    m.append('x')
                elif i == 1 and j == 2:
                    m.append('x')
                elif i == 2 and j == 1:
                    m.append('s')
                elif i == 2 and j == 2:
                    m.append('s')
        elif w0 == 0 and w1 >= 2:
            for (i, j) in zip(mx[0], mx[1]):
                if i == 0 and j == 1:
                    m.append('u')
                elif i == 0 and j == 2:
                    m.append('x')
                elif i == 1 and j == 1:
                    m.append('x')
                elif i == 2 and j == 1:
                    m.append('x')
                elif i == 1 and j == 2:
                    m.append('s')
                elif i == 2 and j == 2:
                    m.append('s')
        elif w0 == 1 and w1 >= 2:
            for (i, j) in zip(mx[0], mx[1]):
                if j == 1:
                    m.append('x')
                elif j == 2:
                    m.append('s')
        elif w0 >= 2 and w1 == 1:
            for (i, j) in zip(mx[0], mx[1]):
                if i == 1:
                    m.append('x')
                elif i == 2:
                    m.append('s')
        elif w0 == 1 and w1 == 0:
            for (i, j) in zip(mx[0], mx[1]):
                if j == 0:
                    m.append('x')
                elif j == 1:
                    m.append('s')
                elif j == 2:
                    m.append('s')
        elif w0 == 0 and w1 == 1:
            for (i, j) in zip(mx[0], mx[1]):
                if i == 0:
                    m.append('x')
                if i == 1:
                    m.append('s')
                if i == 2:
                    m.append('s')
    return m


def strip_numbers(x):
    xj = '.'.join(x)
    xl = re.split('0|1|2', xj)
    xjx = ''.join(xl)
    xlx = xjx.split('.')
    return xlx


def last_stressed_vowel(word, pron, d):
    # Again finds the pronunciation with the shortest syllable
    # count. This could be passed as a variable since it has
    # already been calculated in the rhyme_finder function
    # if len(d[word]) <= 1:
    # 	pron = d[word][0]
    # else:
    # 	p0 = d[word][0]
    # 	p1 = d[word][1]
    # 	sj0 = ''.join(p0)
    # 	sl0 = re.split('0|1|2', sj0)
    # 	sj1 = ''.join(p1)
    # 	sl1 = re.split('0|1|2', sj1)
    # 	if len(sl1) < len(sl0):
    # 		pron = p1
    # 	else:
    # 		pron = p0
    # # Get a list of stressed/unstressed vowels
    mtr = meter(word, d)
    vowel_index = []
    # Find the index of the last stressed vowel. This is very
    # verbose, could easily be reduced.
    if len(mtr) == 1:
        lsv = -1
    elif mtr[-1] == 's' or mtr[-1] == 'x':
        lsv = -1
    elif mtr[-2] == 's' or mtr[-3] == 'x':
        lsv = -2
    elif mtr[-3] == 's' or mtr[-3] == 'x':
        lsv = -3
    elif mtr[-4] == 's' or mtr[-4] == 'x':
        lsv = -4
    elif mtr[-5] == 's' or mtr[-5] == 'x':
        lsv = -5
    elif mtr[-6] == 's' or mtr[-6] == 'x':
        lsv = -6
    elif mtr[-7] == 's' or mtr[-7] == 'x':
        lsv = -7
    elif mtr[-8] == 's' or mtr[-8] == 'x':
        lsv = -8
    elif mtr[-9] == 's' or mtr[-9] == 'x':
        lsv = -9
    elif mtr[-10] == 's' or mtr[-10] == 'x':
        lsv = -10
    else:
        lsv = -1
    # Create list of the index of vowels within pronunciation
    for i in pron:
        if '0' in i or '1' in i or '2' in i:
            vowel_index.append(pron.index(i))
        else:
            continue
    # Return the index of the last stressed vowel within the pronunciation
    return vowel_index[lsv]


def rhyme_finder(word, tokenized_text, d):
    # Find all pronunciations of text from cmudict and store
    # in a list of sets
    word_list = make_word_list(tokenized_text, d)
    rhyming_words = []
    # If only one pronunciation, use that
    if len(d[word]) <= 1:
        pron = d[word][0]
    # Otherwise search for the pronunciation with the fewest
    # number of syllables and use that. This should eliminate
    # spaces before evaluation
    else:
        p0 = d[word][0]
        p1 = d[word][1]
        sj0 = ''.join(p0)
        sl0 = re.split('0|1|2', sj0)
        sj1 = ''.join(p1)
        sl1 = re.split('0|1|2', sj1)
        if len(sl1) < len(sl0):
            pron = p1
        else:
            pron = p0
    # Remove syllable indicating numbers from pronunciation
    pronS = strip_numbers(pron)
    # Get the index of the last stressed vowel within pronunciation
    lsv = last_stressed_vowel(word, pron, d)
    # Rhyme part equals list of all elements of the pronunciation
    # that follow the last stressed vowel
    rhyme_part = pronS[lsv:]
    # Get the negative of the number of elements that follow lsv
    lrp = len(rhyme_part) * -1
    # For every word, pronunciation in text
    for (x, y) in word_list:
        # Remove vowel breakpoints
        ps = strip_numbers(y)
        # If the pronunciation of the last few elements is equal to
        # the rhyming elements of word then they are rhyming words
        if ps[lrp:] == rhyme_part and ps[lrp-1:] != pronS[lsv-1:]:
            rhyming_words.append(x)
        else:
            pass
    # Check that rhymes are not equal to the original word
    rw = [i for i in rhyming_words if not i == word]
    # Return list of rhyming words
    return rw
