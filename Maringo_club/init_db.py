import sqlite3

conn = sqlite3.connect('your_database.db')
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT
)
''')

# Create registrations table
c.execute('''
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    dob TEXT,
    sport TEXT,
    gender TEXT,
    kin TEXT,
    email TEXT,
    phone TEXT,
    county TEXT,
    height TEXT,
    weight TEXT,
    special_needs TEXT,
    enrolment TEXT
)
''')

conn.commit()
conn.close()
print("Database and tables created successfully.")
