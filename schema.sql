CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_on TEXT DEFAULT (datetime('now')),
    slug TEXT NOT NULL UNIQUE,
    status INTEGER DEFAULT 0,
    title TEXT NOT NULL,
    updated_on TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(author_id) REFERENCES users(id)
);