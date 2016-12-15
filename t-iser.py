import nltk

t =  open('lyrics_verse.txt')


u = []

job_titles = [line.strip().rsplit(None, 1)[-1] for line in t.readlines()]

for i in job_titles:
    b = nltk.word_tokenize(i)
    u.extend(b)

punc = set([',','.','"',"''","'",'?','!'])

for i in u:
    if i in punc:
        u.remove(i)

u = set(u)
u = list(u)
print (u)
