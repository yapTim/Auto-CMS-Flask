CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
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

CREATE TABLE cars (
    id INTEGER PRIMARY KEY,
    model TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    created_on TEXT DEFAULT (datetime('now')),
    updated_on TEXT DEFAULT (datetime('now')),
    status INTEGER DEFAULT 0,
    series TEXT NOT NULL,
    transmission INTEGER NOT NULL DEFAULT 0,
    car_type INTEGER NOT NULL DEFAULT 0,
    fuel INTEGER DEFAULT 0
);

CREATE TABLE trucks (
    id INTEGER PRIMARY KEY,
    model TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    created_on TEXT DEFAULT (datetime('now')),
    updated_on TEXT DEFAULT (datetime('now')),
    status INTEGER DEFAULT 0,
    size INTEGER DEFAULT 0,
    weight_category INTEGER DEFAULT 0
);

INSERT INTO
    users(email, first_name, last_name, password, username)
VALUES
    ('test@admin.com', 'Test', 'Admin', 'pass', 'admin');
