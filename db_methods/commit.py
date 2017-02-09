import sqlite3

conn = sqlite3.connect('app.db')

filed = open('files/rhyme_dict_verse.txt', 'r')
file_content = filed.read()
filed.close()

c = conn.cursor()

c.execute("INSERT INTO source_rhymes VALUES (?, ?, ?)", (002, 'rhymes_verse', buffer(file_content)))

conn.commit()
conn.close()
