import sqlite3

conn = sqlite3.connect('your_database.db')
with open('users.sql') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
