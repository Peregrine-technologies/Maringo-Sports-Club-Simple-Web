CREATE TABLE IF NOT EXISTS game_registration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    dob DATE,
    sport TEXT,
    gender TEXT,
    kin TEXT,
    phone TEXT,
    county TEXT,
    height INTEGER,
    weight INTEGER,
    special_needs TEXT,
    enrolment_type TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
