import sqlite3


# Constants
DRAFT = 0
PUBLISHED = 1


def init_db(app):
    """ Initialize tables if they do not exist """
    query = '''
        SELECT name FROM sqlite_master WHERE type="table" AND name IN
        ("users", "posts")
    '''
    conn = sqlite3.connect('autocms.sqlite')
    cursor = conn.cursor()
    cursor.execute(query)

    if cursor.fetchone() is None:
        with app.app_context():
            with app.open_resource('schema.sql', mode='r') as f:
                cursor.executescript(f.read())
            conn.commit()


def fetch_list(db, query):
    cursor = db.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    return data


# conn = sqlite3.connect('autocms.sqlite')
# conn.row_factory = sqlite3.Row
# cur = conn.cursor()

# cur.execute('SELECT posts.*, users.* FROM posts INNER JOIN users ON posts.author_id = users.id')
# x = cur.fetchone()
# print(dict(x))
