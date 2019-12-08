CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    password TEXT,
    username TEXT
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    slug TEXT NOT NULL,
    updated_on TEXT DEFAULT (datetime('now')),
    content TEXT,
    created_on TEXT DEFAULT (datetime('now')),
    status INTEGER,
    author_id INTEGER,
    FOREIGN KEY(author_id) REFERENCES users(id)
);